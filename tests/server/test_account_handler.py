# test_route_dispatcher
#
# test the functionality of the route dispatcher

import pytest

from starling_server.handlers.account import Account
from starling_server.handlers.account_handler import AccountHandler
from starling_server.schemas import AccountSchema, AccountBalanceSchema


class TestInitialise:
    def test_initialise_account_handler(self, testdb_with_real_accounts):
        # GIVEN a database initialised with real accounts
        account_handler = AccountHandler(testdb_with_real_accounts)

        # WHEN I get the accounts
        accounts = account_handler.accounts

        # THEN the accounts have been initialised correctly
        assert isinstance(accounts, list)
        assert isinstance(accounts[0], Account)


class TestAccounts:
    @pytest.mark.asyncio
    async def test_get_accounts(self, testdb_with_real_accounts):
        # GIVEN a dispatcher with a test database initialised with Starling accounts
        account_handler = AccountHandler(testdb_with_real_accounts)

        # WHEN I get the accounts
        accounts = await account_handler.get_accounts()

        # THEN the accounts are returned
        assert isinstance(accounts, list)
        assert len(accounts) > 0
        for account in accounts:
            assert isinstance(account, AccountSchema)

    @pytest.mark.asyncio
    async def test_get_account_balances(self, testdb_with_real_accounts):
        # GIVEN a dispatcher with a test database initialised with Starling accounts
        account_handler = AccountHandler(testdb_with_real_accounts)

        # WHEN I get the account balances
        balances = await account_handler.get_account_balances()

        # THEN the account balances are returned
        assert isinstance(balances, list)
        assert len(balances) > 0
        for balance in balances:
            assert isinstance(balance, AccountBalanceSchema)
