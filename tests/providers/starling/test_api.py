from datetime import datetime, timedelta

import pytest

from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema


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
    @pytest.mark.asyncio
    async def test_get_transactions_between(self, api, account):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        transactions = await api.get_transactions_between(
            account.uuid, start_date, end_date
        )
        assert isinstance(transactions, list)
        assert isinstance(transactions[0], TransactionSchema)
