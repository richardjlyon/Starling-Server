# providers/starling/test_api_v2.py
#
# tests the functionality of the StarlingAPI class
import uuid
from datetime import datetime, timedelta

import pytest

from starling_server.providers.starling.api import StarlingProvider
from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema


class TestInitialisation:
    def test_initialise_all_parameters(self, config):
        # GIVEN a config file

        # WHEN I initialise an api provider with all properties
        api = StarlingProvider(
            auth_token=config.token,
            bank_name=config.bank_name,
            account_uuid=config.account_uuid,
        )
        # THEN the provider initialises properly
        assert api.auth_token == config.token
        assert api.bank_name == config.bank_name
        assert api.account_uuid == config.account_uuid

    def test_initialise_token_only(self, config):
        # GIVEN a config file

        # WHEN I initialise an api provider only with a token
        api = StarlingProvider(auth_token=config.token)

        # THEN provider initialises correctly
        assert api.auth_token == config.token
        assert api.bank_name is None
        assert api.account_uuid is None

    def test_initialse_without_bank_name_raises(self, config):
        # GIVEN a config file
        # WHEN I initialise an api provider with an account id but not a bank name
        # THEN it raises value error
        with pytest.raises(ValueError) as e:
            StarlingProvider(auth_token=config.token, account_uuid=config.account_uuid)


class TestAccount:
    @pytest.mark.asyncio
    async def test_get_accounts(self, config):
        # GIVEN an api initialised only with an access token
        api = StarlingProvider(auth_token=config.token, bank_name=config.bank_name)

        # WHEN I get the accounts
        accounts = await api.get_accounts()

        # THEN the accounts are correct
        assert isinstance(accounts, list)
        assert len(accounts) > 0
        assert isinstance(accounts[0], AccountSchema)

    @pytest.mark.asyncio
    async def test_get_account_balance(self, config):
        # GIVEN an api initialised with a personal account id
        api = StarlingProvider(
            auth_token=config.token,
            bank_name=config.bank_name,
            account_uuid=config.account_uuid,
        )

        # WHEN I get account balance
        balance = await api.get_account_balance()

        # THEN I get the account balance
        assert isinstance(balance, AccountBalanceSchema)


class TestTransaction:
    @pytest.mark.asyncio
    async def test_get_transactions_between(self, config):
        # GIVEN an api initialised with a personal account id
        api = StarlingProvider(
            auth_token=config.token,
            bank_name=config.bank_name,
            account_uuid=config.account_uuid,
        )

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
    async def test_insert(self, category_helper, config):
        # GIVEN a config filepath
        helper = category_helper

        # WHEN I insert an account
        await helper.insert(config.token, config.account_uuid, config.bank_name)

        # THEN the config file is updated with an account id / default category pair
        config_file = helper._load()
        assert str(config.account_uuid) in config_file
        default_category_uuid = uuid.UUID(config_file[str(config.account_uuid)])
        assert isinstance(default_category_uuid, uuid.UUID)

    @pytest.mark.asyncio
    async def test_category_for_account_id(self, category_helper, config):
        # GIVEN a config file with a account id / default category pair
        helper = category_helper
        await helper.insert(config.token, config.account_uuid, config.bank_name)

        # WHEN I get the default category
        default_category = helper._category_for_account_id(config.account_uuid)

        # THEN the default category is correct
        expected_default_category = uuid.UUID("b23c9e8b-4377-4d9a-bce3-e7ee5477af50")
        assert default_category == expected_default_category

    @pytest.mark.asyncio
    async def test_category_for_account_id_none(self, category_helper, config):
        # GIVEN a config file with a account id / default category pair
        helper = category_helper
        await helper.insert(config.token, config.account_uuid, config.bank_name)

        # WHEN I get the default category for None
        default_category = helper._category_for_account_id(account_uuid=None)

        # THEN
        default_category = None
