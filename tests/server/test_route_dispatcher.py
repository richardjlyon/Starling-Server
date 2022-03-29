# test_route_dispatcher
#
# test the functionality of the route dispatcher

import pytest

from starling_server.server.account import Account
from starling_server.server.route_dispatcher import (
    RouteDispatcher,
    get_latest_transaction_time,
)
from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema
from tests.conftest import select_transactions


class TestAccounts:
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


class TestGetNewTransactions:
    def test_get_latest_transaction_time(self, db_4_transactions):
        # GIVEN a test database with transactions of different time stamps
        # WHEN I get the latest transaction time
        database = None
        account_uuid = None
        latest_transaction_time = get_latest_transaction_time(database, account_uuid)

        # THEN the latest transaction time is returned
        expected_transaction_time = None
        assert latest_transaction_time == expected_transaction_time

    @pytest.mark.asyncio
    async def test_get_new_transactions(self, testdb_with_real_accounts):
        print(testdb_with_real_accounts.select_accounts())
        accounts = [
            Account(account_schema)
            for account_schema in testdb_with_real_accounts.select_accounts(
                as_schema=True
            )
        ]
        print(accounts)


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
