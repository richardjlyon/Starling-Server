"""Comment at the top

route_dispatcher.py

A class for coordinating data fetch, storage, and publishing
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Any, Coroutine

from starling_server.config import default_interval_days
from starling_server.db.edgedb.database import Database
from starling_server.providers.provider_api import ProviderAPI
from starling_server.server.config_helper import get_class_for_bank_name
from starling_server.server.schemas.account import AccountBalanceSchema, AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema


class APIFactory:
    """Creates a list of api objects for the accounts in a database."""

    db: Database
    apis: List[ProviderAPI]

    def __init__(self, db: Database):
        self.db = db
        self.apis = self.make_apis()

    def make_apis(self) -> List[ProviderAPI]:
        """Returns a list of account api objects for each bank in the database."""
        banks_db = self.db.client.query(
            """
            select Bank {
                name,
                auth_token_hash,
                accounts: {
                    uuid
                }
            }
            """
        )

        api_list = []
        for bank in banks_db:
            for account in bank.accounts:
                api_class: ProviderAPI = get_class_for_bank_name(bank.name)
                api_list.append(
                    api_class(
                        auth_token=bank.auth_token_hash,
                        account_uuid=account.uuid,
                        bank_name=bank.name,
                    )
                )

        return api_list

    def get_api_for_id(self, account_uuid: uuid.UUID) -> Optional[ProviderAPI]:
        """Returns the account with the given id, or None."""
        return next(api for api in self.apis if api.account_uuid == account_uuid)


class RouteDispatcher:
    """Controls server operations to coordinate fetching, storage, and publishing."""

    db: Database
    api_list: APIFactory

    def __init__(self, database: Database):
        self.db = database
        self.api_list = APIFactory(database)

    # = ACCOUNTS =======================================================================================================

    async def get_accounts(self) -> List[AccountSchema]:
        """Get a list of accounts from the database.

        Args:
            force_refresh (bool): If true, force update of account details from the provider

        Returns:
            A list of `AccountSchema` objects
        """
        return self.db.select_accounts(as_schema=True)

    async def get_account_balances(
        self,
    ) -> List[Coroutine[Any, Any, AccountBalanceSchema]]:
        """Get a list of account balances from the provider."""
        balances = []
        for api in self.api_list.apis:
            balances.append(await api.get_account_balance())
        return balances

    # = TRANSACTIONS ===================================================================================================

    async def get_transactions_for_account_id_between(
        self,
        account_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[List[TransactionSchema]]:
        """Get transactions for the specified account for the default time interval."""

        # FIXME Tidy this logic up include start_date OR end_date
        # TODO start_date is earliest of (start_date / account_last_updated)
        if start_date or end_date is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=default_interval_days)

        # get latest transactions
        api = self.api_list.get_api_for_id(account_id)
        transactions = await api.get_transactions_between(start_date, end_date)

        # save to the database
        for transaction in transactions:
            # counter_party = make_counterparty_from(transaction)
            self.db.upsert_transaction(transaction)

        print(len(transactions))
        return transactions

    async def get_transactions_between(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Optional[List[TransactionSchema]]:

        transactions = []
        for account in self.db.select_accounts(as_schema=True):
            result = await self.get_transactions_for_account_id_between(
                account_id=account.uuid, start_date=start_date, end_date=end_date
            )
            transactions.extend(result)

        transactions.sort(key=lambda t: t.time, reverse=True)
        return transactions
