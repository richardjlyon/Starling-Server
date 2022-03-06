from typing import List

import server.database as db
from providers.starling.api import API as StarlingAPI
from server.schemas.account import AccountBalanceSchema, AccountSchema

banks = [
    StarlingAPI(bank_name="personal"),
    StarlingAPI(bank_name="business"),
]


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
        await db.save_accounts(accounts)

        return accounts

    @staticmethod
    async def get_account_balances() -> List[AccountBalanceSchema]:
        """Get a list of account balances from the provider."""

        balances = []
        for bank in banks:
            for account in await bank.get_accounts():
                print(account)
                balances.append(await bank.get_account_balance(account.uuid))

        return balances
