# from datetime import datetime, timedelta, timezone
#
# import pytest
#
# from starling_server.server.handlers.transaction_handler import (
#     TransactionHandler,
# )
#
#
# class TestGetNewTransactions:
#     @pytest.mark.skip(reason="not sure how to implement this")
#     def test_get_latest_transaction_time(self, db_with_transactions):
#         # GIVEN a test database with transactions of different time stamps
#
#         # FIXME this won't work as TransactionHandler can't be initialised with dummy accounts
#         handler = TransactionHandler(db_with_transactions)
#         account = handler.accounts[0]
#         expected_transaction_time = datetime(2020, 1, 1, 7, 1, tzinfo=timezone.utc)
#
#         # WHEN I get the latest transaction time of the first account
#         latest_transaction_time = get_latest_transaction_time(
#             db_with_transactions, account
#         )
#
#         # THEN the latest transaction time is returned
#         assert expected_transaction_time == latest_transaction_time - timedelta(
#             milliseconds=1
#         )
#
#     @pytest.mark.skip(reason="not sure how to implement this")
#     @pytest.mark.asyncio
#     async def test_get_new_transactions(self, db_with_transactions):
#         # GIVEN a test database with transactions
#
#         # WHEN I get the new transactions
#
#         # THEN ???
#
#         pass
#
#
# class TestTransactions:
#     @pytest.mark.skip("reason=not implemented")
#     @pytest.mark.asyncio
#     async def test_get_transactions_for_account_id_between(
#         self, testdb_with_real_accounts, config
#     ):
#         # GIVEN a dispatcher with a test database initialised with Starling accounts and no transactions
#         dispatcher = RouteDispatcher(database=testdb_with_real_accounts)
#         transactions = select_transactions(testdb_with_real_accounts)
#         assert len(transactions) == 0
#
#         # WHEN I get transactions for an account with the given uuid
#         transactions = await dispatcher.get_transactions_for_account_id_between(
#             account_id=config.account_uuid
#         )
#
#         # THEN the transactions are returned
#         assert isinstance(transactions, list)
#         assert isinstance(transactions[0], TransactionSchema)
#
#         # AND the database is updated
#         transactions = select_transactions(testdb_with_real_accounts)
#         assert len(transactions) > 0
#
#     @pytest.mark.asyncio
#     @pytest.mark.skip(
#         reason="Need to modify config to load more than one account in test database"
#     )
#     async def test_get_transactions_between(self, live_dispatcher, personal_account_id):
#         # GIVEN a test database initialised with Starling accounts and no transactions
#         transactions = select_transactions()
#         assert len(transactions) == 0
#
#         # WHEN I get transactions
#         transactions = await live_dispatcher.get_transactions_between()
#
#         # THEN the transactions are returned
#         assert isinstance(transactions, list)
#         assert isinstance(transactions[0], TransactionSchema)
#
#         # AND the database is updated
#         transactions = select_transactions(live_dispatcher)
#         assert len(transactions) > 0
#
#         # AND there are transactions from both accounts
#         pass  # FIXME
