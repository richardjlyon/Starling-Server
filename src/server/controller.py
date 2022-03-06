from providers.starling.api import get_token_for_type_name, api_get_balance
from server.database import retrieve_accounts
from server.models.account import AccountBalanceSchema


class Controller:
    """Controls server operations to coordinate fetch, storage, and publishing."""

    async def get_accounts(self):
        """Get a list of accounts from the provider and save to the database."""
        return await retrieve_accounts()

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
