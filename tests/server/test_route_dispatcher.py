# test_route_dispatcher
#
# test the functionality of the route dispatcher

import pytest

from starling_server.server.route_dispatcher import RouteDispatcher
from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema
from tests.db.database.conftest import select_transactions


# def test_initialise():
#     # GIVEN a dispatcher and the live database
#     dispatcher = RouteDispatcher(db)
#
#     # WHEN I get the providers
#     providers = dispatcher.providers
#
#     # THEN there are valid account api objects
#     assert len(providers) > 0
#     for provider in providers:
#         assert provider.account_uuid is not None
#         assert provider.bank_name is not None
#         assert provider.auth_token is not None


class TestAccounts:
    @pytest.mark.skip("reason=not implemented")
    @pytest.mark.asyncio
    async def test_get_accounts(self, testdb_with_real_accounts):
        # GIVEN a dispatcher with a test database initialised with Starling accounts
        dispatcher = RouteDispatcher(database=testdb_with_real_accounts)

        # WHEN I get the accounts
        accounts = await dispatcher.get_accounts()

        # THEN the accounts are returned
        assert isinstance(accounts, list)
        assert len(accounts) > 0
        for account in accounts:
            assert isinstance(account, AccountSchema)

    @pytest.mark.skip("reason=not implemented")
    @pytest.mark.asyncio
    async def test_get_account_balances(self, testdb_with_real_accounts):
        # GIVEN a dispatcher with a test database initialised with Starling accounts
        dispatcher = RouteDispatcher(database=testdb_with_real_accounts)

        # WHEN I get the account balances
        balances = await dispatcher.get_account_balances()

        # THEN the account balances are returned
        assert isinstance(balances, list)
        assert len(balances) > 0
        for balance in balances:
            assert isinstance(balance, AccountBalanceSchema)


class TestTransactions:
    @pytest.mark.skip("reason=not implemented")
    @pytest.mark.asyncio
    async def test_get_transactions_for_account_id_between(
        self, testdb_with_real_accounts, config
    ):
        # GIVEN a dispatcher with a test database initialised with Starling accounts and no transactions
        dispatcher = RouteDispatcher(database=testdb_with_real_accounts)
        transactions = select_transactions(testdb_with_real_accounts)
        assert len(transactions) == 0

        # WHEN I get transactions for an account with the given uuid
        transactions = await dispatcher.get_transactions_for_account_id_between(
            account_id=config.account_uuid
        )

        # THEN the transactions are returned
        assert isinstance(transactions, list)
        assert isinstance(transactions[0], TransactionSchema)

        # AND the database is updated
        transactions = select_transactions(testdb_with_real_accounts)
        assert len(transactions) > 0

    @pytest.mark.asyncio
    @pytest.mark.skip(
        reason="Need to modify config to load more than one account in test database"
    )
    async def test_get_transactions_between(self, live_dispatcher, personal_account_id):
        # GIVEN a test database initialised with Starling accounts and no transactions
        transactions = select_transactions()
        assert len(transactions) == 0

        # WHEN I get transactions
        transactions = await live_dispatcher.get_transactions_between()

        # THEN the transactions are returned
        assert isinstance(transactions, list)
        assert isinstance(transactions[0], TransactionSchema)

        # AND the database is updated
        transactions = select_transactions(live_dispatcher)
        assert len(transactions) > 0

        # AND there are transactions from both accounts
        pass  # FIXME
