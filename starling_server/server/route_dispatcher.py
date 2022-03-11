from datetime import datetime
from typing import List, Optional

from loguru import logger

from starling_server.db.db_base import DBBase
from starling_server.providers.starling.api import API as StarlingAPI
from starling_server.server.schemas.account import AccountBalanceSchema, AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema


class RouteDispatcher:
    """Controls server operations to coordinate fetching, storage, and publishing."""

    def __init__(self, database: DBBase, banks: Optional[List[StarlingAPI]] = None):
        self.db = database
        self.banks = banks

    async def get_accounts(self, force_refresh: bool = False) -> List[AccountSchema]:
        """Get a list of accounts from the database.

        Args:
            force_refresh (): If true, force update of account details from the provider
        """
        accounts = self.db.get_accounts()
        if len(accounts) == 0 or force_refresh:
            await self.update_banks_and_accounts()

        return self.db.get_accounts(as_schema=True)

    async def update_banks_and_accounts(self):
        """Update the database with bank and account details obtained from the provider."""
        for bank in self.banks:
            accounts = await bank.get_accounts()
            for account in accounts:
                self.db.insert_or_update_account(account)

        logger.info(f"Updated accounts from bank details")

    async def get_account_balances(self) -> List[AccountBalanceSchema]:
        """Get a list of account balances from the provider."""

        accounts = self.db.get_accounts()
        balances = []
        for account in accounts:
            print(account)
            bank = StarlingAPI(bank_name=account.bank.name)
            balances.append(await bank.get_account_balance(account_uuid=account.uuid))

        return balances

    async def get_transactions_between(
        self,
        account_id: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> Optional[List[TransactionSchema]]:

        """Get transactions for the specified account for the default time interval."""

        # get latest transactions
        bank = await get_bank_for_account_id(account_id)
        if bank is None:
            return []
        transactions = await bank.get_transactions_between(
            account_id, start_date, end_date
        )

        # save to the database

        return transactions


# = HELPERS ===========================================================================================================


async def get_bank_for_account_id(account_id: str) -> Optional[StarlingAPI]:
    the_bank = None
    for bank in self.banks:  # TODO Ask Alex - shorter way of doing this?
        accounts = await bank.get_accounts() if bank.accounts is None else bank.accounts
        if (
            next(
                (account for account in accounts if account.uuid == account_id),
                None,
            )
            is not None
        ):
            the_bank = bank
            break

    return the_bank
