import pytest

from server.schemas.account import AccountSchema, AccountBalanceSchema


class TestAccount:
    def test_initialise_token(self, api):
        assert isinstance(api.token, str)

    @pytest.mark.asyncio
    async def test_get_accounts(self, api):
        accounts = await api.get_accounts()
        assert isinstance(accounts, list)
        assert isinstance(accounts[0], AccountSchema)

    @pytest.mark.asyncio
    async def test_get_account_balance(self, api, account):
        balance = await api.get_account_balance(account.uuid)
        assert isinstance(balance, AccountBalanceSchema)


class TestTransaction:
    pass
