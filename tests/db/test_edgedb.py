from tests.db.conftest import (
    make_accounts,
    select_accounts,
    make_transactions,
    insert_2_accounts,
    select_transactions,
)


class TestAccount:
    def test_insert_or_update_account_insert_2(self, db):
        # GIVEN an empty database
        # WHEN I add two accounts
        # THEN two accounts are added
        accounts = make_accounts(2)
        for account in accounts:
            db.insert_or_update_account(account)

        accounts_db = select_accounts()
        assert len(accounts_db) == 2
        assert accounts_db[0].bank.name == accounts[0].bank_name

        # show(accounts_db, "Accounts")

    def test_insert_or_update_account_update_1(self, db):
        # GIVEN a database with two accounts
        # WHEN I update an account name
        # THEN the account name is updated

        # insert two accounts
        accounts = make_accounts(2)
        for account in accounts:
            db.insert_or_update_account(account)

        # accounts_db = select_accounts()
        # show(accounts_db, "Accounts before update")

        # change 1 account name and update database
        modified_account_name = f"{accounts[0].account_name} **MODIFIED**"
        accounts[0].account_name = modified_account_name
        for account in accounts:
            db.insert_or_update_account(account)

        # check only modified account has changed
        accounts_db = select_accounts()
        # show(accounts_db, "Accounts after update")

        assert len(accounts_db) == 2
        assert accounts_db[0].name == modified_account_name

    def test_get_accounts(self, db):
        # GIVEN a database with two accounts
        # WHEN I get the accounts
        # THEN the accounts are correct
        # insert two accounts

        # configure the database
        accounts = make_accounts(2)
        for account in accounts:
            db.insert_or_update_account(account)

        # test
        accounts = db.get_accounts(as_schema=True)
        assert isinstance(accounts, list)
        # assert isinstance(accounts[0], AccountSchema) # FIXME Why does this fail?


class TestTransaction:
    def test_insert_or_update_transaction_insert_2(self, db):
        # GIVEN a database with two accounts with no transactions
        # WHEN I insert transactions in each account
        # THEN the transactions are inserted

        insert_2_accounts(db)
        accounts_db = select_accounts()
        # show(accounts_db, "Accounts before update")

        # insert test transactions
        accounts_db = select_accounts()
        for account_db in accounts_db:
            transactions = make_transactions(2, account_uuid=account_db.uuid)
            for transaction in transactions:
                db.insert_or_update_transaction(transaction)

        accounts_db = select_accounts()
        transactions_db = select_transactions()

        # show(accounts_db, "Accounts after inserting transactions")
        # show(transactions_db, "Transactions")

        # confirm all transactions were added
        assert len(transactions_db) == 4

        # confirm they were added to the right accounts
        for account_db in accounts_db:
            assert len(account_db.transactions) == 2
            account_uuid = str(account_db.uuid)
            for transaction_db in account_db.transactions:
                reference = transaction_db.reference
                assert account_uuid[-4:] == reference[0:4]  # see `make_transactions()`

    def test_insert_or_update_transaction_update_1(self, db):
        # GIVEN a database with 2 accounts of 2 transactions each
        # WHEN I update a transaction
        # THAT transaction is updated and the others are unaffected

        # create accounts and transactions
        transactions = []
        insert_2_accounts(db)
        accounts_db = select_accounts()
        for account_db in accounts_db:
            account_transactions = make_transactions(2, account_uuid=account_db.uuid)
            transactions.extend(account_transactions)
            for transaction in account_transactions:
                db.insert_or_update_transaction(transaction)

        transactions_db = select_transactions()

        # change 1 transaction and update
        modified_transaction_reference = f"{transactions_db[0].reference} **MODIFIED**"
        transactions[0].reference = modified_transaction_reference
        for transaction in transactions:
            db.insert_or_update_transaction(transaction)

        # verify only modified transaction has changed
        transactions_db = select_transactions()
        assert "**MODIFIED**" in transactions_db[0].reference

        # show(transactions_db)
