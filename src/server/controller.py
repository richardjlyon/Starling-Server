from datetime import datetime
from typing import List, Optional

from db.edgedb.database import Database
from providers.starling.api import API as StarlingAPI
from server.schemas.account import AccountBalanceSchema, AccountSchema
from server.schemas.transaction import TransactionSchema

banks = [
    StarlingAPI(bank_name="Starling Personal"),
    StarlingAPI(bank_name="Starling Business"),
]

db = Database()


class Controller:
    """Controls server operations to coordinate fetch, storage, and publishing."""

    @staticmethod
    async def get_accounts() -> List[AccountSchema]:
        """Get a list of accounts from the provider and save to the database."""

        # fetch data from bank
        accounts = []
        for bank in banks:
            for account in await bank.get_accounts():
                accounts.append(account)

        # update database
        for account in accounts:
            db.save_account(account)

        return accounts

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
