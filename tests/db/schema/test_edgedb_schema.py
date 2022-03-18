"""
These tests verify the integrity of the EdgeDB schema. They require database "test" in the edgedb instance.
"""
import uuid

from tests.db.schema.conftest import (
    test_bank_name,
    insert_bank,
    insert_account,
    insert_transaction,
    insert_categories,
)


class TestBank:
    def test_insert_bank(self, db):
        # GIVEN an initialised database
        # WHEN I insert a bank
        insert_bank(db, test_bank_name)

        # THEN the bank is inserted
        bank_name = db.query("Select Bank.name")[0]
        assert bank_name == test_bank_name

    def test_delete_bank(self, db):
        # GIVEN a db with a bank and two accounts
        insert_bank(db, test_bank_name)
        for account_name in ["Personal Account 1", "Personal Account 2"]:
            insert_account(db, account_name)

        # WHEN I delete the bank
        db.query("delete Bank filter .name = <str>$name", name=test_bank_name)

        # THEN the bank and accounts are deleted
        assert len(db.query("select Bank")) == 0
        assert len(db.query("select Account")) == 0


class TestCategory:
    def test_insert_categories(self, db):
        # GIVEN an empty database
        # WHEN I insert a set of categories and category groups
        insert_categories(db)

        # THEN the categories are inserted
        assert len(db.query("select CategoryGroup")) > 0
        assert len(db.query("Select Category")) > 0
        categories = db.query("Select Category {name, category_group: { name }}")
        assert categories[0].category_group.name == "Mandatory"


class TestAccount:
    def test_insert_accounts(self, db):
        # GIVEN a db with a bank
        insert_bank(db, test_bank_name)

        # WHEN I add two accounts
        for account_name in ["Personal Account 1", "Personal Account 2"]:
            insert_account(db, account_name)

        # THEN the two counts have been inserted
        accounts = db.query("Select Account{bank:{name}}")
        assert len(accounts) == 2
        # AND they are linked to the bank
        assert accounts[0].bank.name == test_bank_name

    def test_delete_account_with_transactions(self, db_with_transactions):
        # GIVEN a db with 2 accounts and 4 transactions
        assert len(db_with_transactions.query("select Account")) == 2
        assert len(db_with_transactions.query("select Transaction")) == 4

        # WHEN I delete one account
        db_with_transactions.query(
            """
            delete Account
            filter .name = "Personal Account 2"
            """
        )

        # THEN the account and its transactions are deleted
        assert len(db_with_transactions.query("select Account")) == 1
        assert len(db_with_transactions.query("select Transaction")) == 2
        # AND the other account is not
        assert (
            len(
                db_with_transactions.query(
                    "select Account filter .name = 'Personal Account 1'"
                )
            )
            == 1
        )


class TestTransaction:
    def test_insert_transactions(self, db_with_accounts):
        # GIVEN a db with a 2 accounts
        # WHEN I add transactions to the accounts
        account_uuids = db_with_accounts.query("select Account.uuid")
        for account_uuid in account_uuids:
            for i in range(2):
                insert_transaction(db_with_accounts, account_uuid)

        # THEN the transactions are added
        assert len(db_with_accounts.query("select Transaction")) == 4
        # AND are linked to an account
        t_0 = db_with_accounts.query("select Transaction { account: {uuid}}")[0]
        assert isinstance(t_0.account.uuid, uuid.UUID)
