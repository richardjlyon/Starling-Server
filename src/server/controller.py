from datetime import datetime
from typing import List, Optional

from loguru import logger

from db.db_base import DBBase
from src.providers.starling.api import API as StarlingAPI
from src.server.schemas.account import AccountBalanceSchema, AccountSchema
from src.server.schemas.transaction import TransactionSchema

banks = [
    StarlingAPI(bank_name="Starling Personal"),
    StarlingAPI(bank_name="Starling Business"),
]


class Controller:
    """Controls server operations to coordinate fetch, storage, and publishing."""

    def __init__(self, db: DBBase):
        self._db = db

    async def get_accounts(self, force_refresh: bool = False) -> List[AccountSchema]:
        """
        Get a list of accounts from the provider and save to the database.

        If we have stored account data in the database, fetch and return it. Otherwise, get it from the bank, update
        the database, and then return it.

        Args:
            force_refresh (): If true, force update of account details from the provider

        Returns:
            A list of accounts.

        """

        # try and get accounts from the database
        accounts = self._db.get_accounts(as_schema=True)

        # if there are none, or a refresh is forced, get from the bank and update database
        if len(accounts) == 0 or force_refresh:

            for bank in banks:
                accounts = await bank.get_accounts()
                for account in accounts:
                    self._db.insert_or_update_account(account)

            logger.info(f"Retrieved accounts from bank, force_refresh={force_refresh}")

        return self._db.get_accounts(as_schema=True)

    @staticmethod
    async def get_account_balances() -> List[AccountBalanceSchema]:
        """Get a list of account balances from the provider."""

        balances = []
        for bank in banks:
            for account in await bank.get_accounts():
                balances.append(await bank.get_account_balance(account.uuid))

        return balances

    async def get_transactions_between(
        self, account_id: str, start_date: datetime, end_date: datetime
    ) -> Optional[List[TransactionSchema]]:
        """Get transactions for the specified account for the default time interval."""

        # get latest transactions
        bank = await get_bank_for_account_id(account_id)
        if bank is None:
            return
        transactions = await bank.get_transactions_between(
            account_id, start_date, end_date
        )

        # save to the database

        return transactions


# = HELPERS ===========================================================================================================


async def get_bank_for_account_id(account_id: str) -> Optional[StarlingAPI]:
    the_bank = None
    for bank in banks:  # TODO Ask Alex - shorter way of doing this?
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
