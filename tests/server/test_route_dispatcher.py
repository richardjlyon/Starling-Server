# test_route_dispatcher
#
# test the functionality of the route dispatcher


import pytest

from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema
from tests.conftest import select_accounts, select_transactions


class TestAccounts:
    @pytest.mark.asyncio
    async def test_update_banks_and_accounts(self, empty_dispatcher):
        # GIVEN a dispatcher with an empty database and an initialised AccountHelper

        # WHEN I update banks and accounts
        await empty_dispatcher.update_banks_and_accounts()

        # THEN the database is updated with the banks and accounts
        accounts = select_accounts()
        assert len(accounts) > 0

    @pytest.mark.asyncio
    async def test_get_accounts(self, live_dispatcher):
        # GIVEN a test database initialised with Starling accounts

        # WHEN I get the accounts
        accounts = await live_dispatcher.get_accounts()

        # THEN the accounts are returned
        assert isinstance(accounts, list)
        assert isinstance(accounts[0], AccountSchema)

    @pytest.mark.asyncio
    async def test_get_account_balances(self, live_dispatcher):
        # GIVEN a test database initialised with Starling accounts

        # WHEN I get the account balances
        balances = await live_dispatcher.get_account_balances()

        # THEN the account balances are returned
        print(balances)


class TestTransactions:
    @pytest.mark.asyncio
    async def test_get_transactions_for_account_id_between(
        self, live_dispatcher, personal_account_id
    ):
        # GIVEN a test database initialised with Starling accounts and no transactions
        transactions = select_transactions()
        assert len(transactions) == 0

        # WHEN I get transactions for an account with the given uuid
        transactions = await live_dispatcher.get_transactions_for_account_id_between(
            account_id=personal_account_id
        )

        # THEN the transactions are returned
        assert isinstance(transactions, list)
        assert isinstance(transactions[0], TransactionSchema)

        # AND the database is updated
        transactions = select_transactions()
        assert len(transactions) > 0

    @pytest.mark.asyncio
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
        transactions = select_transactions()
        assert len(transactions) > 0

        # AND there are transactions from both accounts
        pass  # FIXME
