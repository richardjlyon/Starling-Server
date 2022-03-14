# test_edgedb.py
#
# Tests the functions of the database class using dummy accounts and transactions

from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema
from tests.conftest import select_accounts, select_transactions
from tests.db.conftest import make_accounts, make_transactions


class TestAccount:
    def test_insert_or_update_account_insert_2(self, empty_db):
        # GIVEN an empty database

        # WHEN I add two accounts
        accounts = make_accounts(2)
        for account in accounts:
            empty_db.insert_or_update_account(account)

        # THEN two accounts are added
        accounts_db = select_accounts()
        assert len(accounts_db) == 2
        assert accounts_db[0].bank.name == accounts[0].bank_name

    def test_insert_or_update_account_update_1(self, db_with_two_accounts):
        # GIVEN a database with two accounts

        # WHEN an account name is modified
        a = select_accounts()[0]
        modified_uuid = a.uuid
        modified_name = a.name + " **MODIFIED**"
        account = AccountSchema(
            uuid=a.uuid,
            bank_name=a.bank.name,
            account_name=modified_name,
            currency=a.currency,
            created_at=a.created_at,
        )
        db_with_two_accounts.insert_or_update_account(account)

        # THEN the account name is updated
        accounts_db = select_accounts()
        account = next(
            account for account in accounts_db if account.uuid == modified_uuid
        )
        assert len(accounts_db) == 2
        assert account.name == modified_name


class TestTransaction:
    def test_insert_or_update_transaction_insert_2(self, db_with_two_accounts):
        # GIVEN a database with two accounts and no transactions

        # WHEN I insert transactions in each account
        accounts_db = select_accounts()
        for account_db in accounts_db:
            transactions = make_transactions(2, account_uuid=account_db.uuid)
            for transaction in transactions:
                db_with_two_accounts.insert_or_update_transaction(transaction)

        # THEN the transactions are inserted
        accounts_db = select_accounts()
        transactions_db = select_transactions()
        assert len(transactions_db) == 4

        # confirm they were added to the right accounts
        for account_db in accounts_db:
            assert len(account_db.transactions) == 2
            account_uuid = str(account_db.uuid)
            for transaction_db in account_db.transactions:
                reference = transaction_db.reference
                assert account_uuid[-4:] == reference[0:4]  # see `make_transactions()`

    def test_insert_or_update_transaction_update_1(self, db_with_four_transactions):
        # GIVEN a database with 2 accounts of 2 transactions each

        # WHEN I update a transaction
        t = select_transactions()[0]
        modified_uuid = t.uuid
        modified_reference = t.reference + " **MODIFIED**"
        transaction = TransactionSchema(
            account_uuid=t.account.uuid,
            uuid=t.uuid,
            time=t.time,
            counterparty_name=t.counterparty_name,
            amount=t.amount,
            reference=modified_reference,
        )
        db_with_four_transactions.insert_or_update_transaction(transaction)

        # THEN transaction is updated
        transactions = select_transactions()
        transaction = next(t for t in transactions if t.uuid == modified_uuid)
        assert "**MODIFIED**" in transaction.reference

    def test_get_transactions_for_account(self, db_with_four_transactions):

        # GIVEN a database with 2 accounts of 2 transactions each

        # WHEN I select the transactions for the personal account
        transactions = select_transactions()
        t0_account_uuid = transactions[0].account.uuid
        t0_uuid = transactions[0].uuid
        transactions = db_with_four_transactions.get_transactions_for_account(
            t0_account_uuid
        )

        # THEN I get the transactions
        assert transactions[0].transactions[0].uuid == t0_uuid

    def test_get_last_transaction_date_for_account(
        self, db_with_four_transactions, personal_account_id
    ):
        # GIVEN a database with 2 accounts of 2 transactions each

        # WHEN I get the last transaction date for the personal account
        last_date = db_with_four_transactions.get_last_transaction_date_for_account(
            personal_account_id
        )

        # THEN the date is for the last transaction
        print(last_date)
