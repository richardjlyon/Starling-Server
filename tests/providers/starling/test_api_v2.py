# providers/starling/test_api_v2.py
#
# tests the functionality of the StarlingAPI class
from datetime import datetime, timedelta

import pytest

from starling_server.providers.starling.api_v2 import APIV2
from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema


class TestAccount:
    @pytest.mark.asyncio
    async def test_get_accounts(self, personal_auth_token):
        # GIVEN an api initialised only with an access token
        api = APIV2(auth_token=personal_auth_token)

        # WHEN I get the accounts
        accounts = await api.get_accounts()

        # THEN the accounts are correct
        assert isinstance(accounts, list)
        assert len(accounts) > 0
        assert isinstance(accounts[0], AccountSchema)

    @pytest.mark.asyncio
    async def test_get_account_balance(self, personal_auth_token, personal_account_id):
        # GIVEN an api initialised with a personal account id
        api = APIV2(auth_token=personal_auth_token, account_uuid=personal_account_id)

        # WHEN I get account balance
        balance = await api.get_account_balance()

        # THEN I get the account balance
        assert isinstance(balance, AccountBalanceSchema)


class TestTransaction:
    @pytest.mark.asyncio
    async def test_get_transactions_between(
        self, personal_auth_token, personal_account_id
    ):
        # GIVEN an api initialised with a personal account id
        api = APIV2(auth_token=personal_auth_token, account_uuid=personal_account_id)

        # WHEN I fetch the transactions between two dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        transactions = await api.get_transactions_between(start_date, end_date)

        # THEN the transactions are correct
        assert isinstance(transactions, list)
        assert len(transactions) > 0
        assert isinstance(transactions[0], TransactionSchema)


class TestCategoryHelper:
    @pytest.mark.asyncio
    async def test_insert(
        self, category_helper, personal_auth_token, personal_account_id
    ):
        # GIVEN a config filepath
        helper = category_helper

        # WHEN I insert an account
        await helper.insert(personal_auth_token, personal_account_id)

        # THEN the config file is updated with a correct account id / default category pair
        expected_default_category = "b23c9e8b-4377-4d9a-bce3-e7ee5477af50"
        config_file = helper._load()
        assert str(personal_account_id) in config_file
        assert config_file[str(personal_account_id)] == expected_default_category

    @pytest.mark.asyncio
    async def test_category_for_account_id(
        self, category_helper, personal_auth_token, personal_account_id
    ):
        # GIVEN a config file with a account id / default category pair
        helper = category_helper
        await helper.insert(personal_auth_token, personal_account_id)

        # WHEN I get the default category
        default_category = helper.category_for_account_id(personal_account_id)

        # THEN the defualt category is corrrect
        expected_default_category = "b23c9e8b-4377-4d9a-bce3-e7ee5477af50"
        assert default_category == expected_default_category

    @pytest.mark.asyncio
    async def test_category_for_account_id_none(
        self, category_helper, personal_auth_token, personal_account_id
    ):
        # GIVEN a config file with a account id / default category pair
        helper = category_helper
        await helper.insert(personal_auth_token, personal_account_id)

        # WHEN I get the default category for None
        default_category = helper.category_for_account_id(account_uuid=None)

        # THEN
        default_category = None
