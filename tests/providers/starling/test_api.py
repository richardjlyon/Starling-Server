# providers/starling/test_api.py
#
# tests the functionality of the StarlingAPI class

from datetime import datetime, timedelta

import pytest

from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema


class TestAccount:
    def test_initialise(self, api_personal_account):
        # GIVEN an initialised api

        # WHEN I get the bank name and token
        # THEN they are correct
        assert api_personal_account.info.account_schema.bank_name == "Starling Personal"
        assert isinstance(api_personal_account.info.token, str)

    @pytest.mark.asyncio
    async def test_get_accounts(self, api_personal_account):
        # GIVEN an initialised api

        # WHEN I fetch the accounts
        accounts = await api_personal_account.get_accounts()

        # THEN the accounts are fetched
        assert isinstance(accounts, list)
        assert isinstance(accounts[0], AccountSchema)

    @pytest.mark.asyncio
    async def test_get_account_balance(self, api_personal_account):
        # GIVEN an initialised api and an account id

        # WHEN I fetch the balance for the account
        balance = await api_personal_account.get_account_balance()

        # THEN I get a balance
        assert isinstance(balance, AccountBalanceSchema)


class TestTransaction:
    @pytest.mark.asyncio
    async def test_get_transactions_between(
        self, api_personal_account, personal_account_id
    ):
        # GIVEN an initialised api and an account id

        # WHEN I fetch the transactions between two dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        transactions = (
            await api_personal_account.get_transactions_for_account_id_between(
                personal_account_id, start_date, end_date
            )
        )

        # THEN I get transactions
        assert isinstance(transactions, list)
        assert isinstance(transactions[0], TransactionSchema)
