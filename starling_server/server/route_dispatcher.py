"""Comment at the top

route_dispatcher.py

A class for coordinating data fetch, storage, and publishing
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Any, Coroutine

from starling_server.config import default_interval_days
from starling_server.db.edgedb.database import Database
from starling_server.server.config_helper import get_class_for_bank_name
from starling_server.server.schemas.account import AccountBalanceSchema, AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema


class RouteDispatcher:
    """Controls server operations to coordinate fetching, storage, and publishing."""

    def __init__(self, database: Database):
        self.db = database
        self.accounts = self._build_account_list()

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
        for account in self.accounts:
            balances.append(await account.get_account_balance())
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
        if start_date or end_date is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=default_interval_days)

        # get latest transactions
        account = self._get_account_for_id(account_id)
        if account is None:
            return

        transactions = await account.get_transactions_between(start_date, end_date)

        # save to the database
        for transaction in transactions:
            self.db.upsert_transaction(transaction)
            # TODO update server_last_updated

        print(len(transactions))
        return transactions

    async def get_transactions_between(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Optional[List[TransactionSchema]]:

        transactions = []
        accounts = self.db.select_accounts(as_schema=True)
        for account in accounts:
            result = await self.get_transactions_for_account_id_between(
                account_id=account.uuid, start_date=start_date, end_date=end_date
            )
            transactions.extend(result)

        transactions.sort(key=lambda t: t.time, reverse=True)
        return transactions

    # = HELPERS ========================================================================================================

    def _build_account_list(self):
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

        accounts = []
        for bank in banks_db:
            for account in bank.accounts:
                api_class = get_class_for_bank_name(bank.name)
                accounts.append(
                    api_class(
                        auth_token=bank.auth_token_hash,
                        account_uuid=account.uuid,
                        bank_name=bank.name,
                    )
                )

        return accounts

    def _get_account_for_id(self, account_uuid: uuid.UUID) -> Optional[Any]:
        """Returns the account with the given id, or None."""
        return next(
            account for account in self.accounts if account.account_uuid == account_uuid
        )
