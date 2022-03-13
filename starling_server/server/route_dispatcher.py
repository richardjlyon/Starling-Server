# route_dispatcher.py
#
# A class for coordinating data fetch, storage, and publishing


import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Any, Coroutine

from starling_server.config import default_interval_days
from starling_server.db.db_base import DBBase
from starling_server.providers.starling.account_helper import AccountHelper
from starling_server.providers.starling.api import API as StarlingAPI
from starling_server.server.schemas.account import AccountBalanceSchema, AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema


class RouteDispatcher:
    """Controls server operations to coordinate fetching, storage, and publishing."""

    def __init__(self, database: DBBase, account_helper: AccountHelper = None):
        self.db = database
        if account_helper is None:
            account_helper = AccountHelper()
        self.helper = account_helper

    # = ACCOUNTS =======================================================================================================

    async def update_banks_and_accounts(self):
        """Update the database with bank and account details obtained from the provider."""
        for info in self.helper.accounts:
            account = AccountSchema(
                uuid=info.account_schema.uuid,
                bank_name=info.account_schema.bank_name,
                account_name=info.account_schema.account_name,
                currency=info.account_schema.currency,
                created_at=info.account_schema.created_at,
            )
            self.db.insert_or_update_account(account)

    async def get_accounts(self, force_refresh: bool = False) -> List[AccountSchema]:
        """Get a list of accounts from the database.

        Args:
            force_refresh (bool): If true, force update of account details from the provider

        Returns:
            A list of `AccountSchema` objects
        """
        accounts = self.db.get_accounts()
        if len(accounts) == 0 or force_refresh:
            await self.update_banks_and_accounts()

        return self.db.get_accounts(as_schema=True)

    async def get_account_balances(
        self,
    ) -> List[Coroutine[Any, Any, AccountBalanceSchema]]:
        """Get a list of account balances from the provider."""

        accounts = self.db.get_accounts()
        balances = []
        for account_db in accounts:
            account = StarlingAPI(account_uuid=account_db.uuid)
            balances.append(await account.get_account_balance())

        return balances

    # = TRANSACTIONS ===================================================================================================

    # FIXME refactor this to get the date of the last transaction, fetch new transactions from that date until
    # now, then return transactions for the defined period
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
        account = StarlingAPI(account_uuid=account_id)
        transactions = await account.get_transactions_for_account_id_between(
            account_id, start_date, end_date
        )

        # save to the database
        for transaction in transactions:
            self.db.insert_or_update_transaction(transaction)

        return transactions

    async def get_transactions_between(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Optional[List[TransactionSchema]]:

        transactions = []
        accounts = self.db.get_accounts(as_schema=True)
        for account in accounts:
            result = await self.get_transactions_for_account_id_between(
                account_id=account.uuid, start_date=start_date, end_date=end_date
            )
            transactions.extend(result)

        transactions.sort(key=lambda t: t.time, reverse=True)
        return transactions

    # = HELPERS ========================================================================================================

    # async def get_bank_for_account_id(self, account_id: str) -> Optional[StarlingAPI]:
    #     accounts = self.db.get_accounts(as_schema=True)
    #     account = next(
    #         (account for account in accounts if account.uuid == account_id),
    #         None,
    #     )
    #
    #     if account is not None:
    #         return StarlingAPI(bank_name=account.bank_name)
    #     else:
    #         return None
