from typing import List

import server.database as db
from providers.starling.api import API as StarlingAPI
from providers.starling.api import get_token_for_type_name, api_get_balance
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

    async def get_account_balances(self):
        """Get a list of account balances from the provider."""
        balances = []
        main_accounts = await self.get_accounts()
        for main_account in main_accounts:
            token = get_token_for_type_name(main_account.type_name)
            for account in main_account.accounts:
                balance = await api_get_balance(token, account.accountUid)
                balances.append(
                    AccountBalanceSchema.from_StarlingBalanceSchema(
                        account_uuid=account.accountUid, balance=balance
                    )
                )
        return balances
