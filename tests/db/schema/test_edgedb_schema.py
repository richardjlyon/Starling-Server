"""
These tests verify the integrity of the EdgeDB schema. They require database "test" in the edgedb instance.
"""
import uuid

from starling_server.schemas.transaction import Counterparty
from tests.conftest import (
    test_bank_name,
    insert_bank,
    insert_account,
    insert_transaction,
    insert_categories,
    upsert_counterparty,
)


class TestBank:
    def test_insert_bank(self, empty_db):
        # GIVEN an initialised database
        # WHEN I insert a bank
        insert_bank(empty_db, test_bank_name)

        # THEN the bank is inserted
        bank_name = empty_db.client.query("Select Bank.name")[0]
        assert bank_name == test_bank_name

    def test_delete_bank(self, empty_db):
        # GIVEN a db with a bank and two accounts
        insert_bank(empty_db, test_bank_name)
        for account_name in ["Personal Account 1", "Personal Account 2"]:
            insert_account(empty_db, account_name)

        # WHEN I delete the bank
        empty_db.client.query(
            "delete Bank filter .name = <str>$name", name=test_bank_name
        )

        # THEN the bank and accounts are deleted
        assert len(empty_db.client.query("select Bank")) == 0
        assert len(empty_db.client.query("select Account")) == 0


class TestCategory:
    def test_insert_categories(self, empty_db):
        # GIVEN an empty database
        # WHEN I insert a set of categories and category groups
        insert_categories(empty_db)

        # THEN the categories are inserted
        assert len(empty_db.client.query("select CategoryGroup")) > 0
        assert len(empty_db.client.query("Select Category")) > 0
        categories = empty_db.client.query(
            "Select Category {name, category_group: { name }}"
        )
        assert categories[0].category_group.name == "Mandatory"


class TestAccount:
    def test_insert_accounts(self, empty_db):
        # GIVEN a db with a bank
        insert_bank(empty_db, test_bank_name)

        # WHEN I add two accounts
        for account_name in ["Personal Account 1", "Personal Account 2"]:
            insert_account(empty_db, account_name)

        # THEN the two counts have been inserted
        accounts = empty_db.client.query("Select Account{bank:{name}}")
        assert len(accounts) == 2
        # AND they are linked to the bank
        assert accounts[0].bank.name == test_bank_name

    def test_delete_account_with_transactions(self, db_with_transactions):
        # GIVEN a db with 2 accounts and 4 transactions
        assert len(db_with_transactions.client.query("select Account")) == 2
        assert len(db_with_transactions.client.query("select Transaction")) == 16

        # WHEN I delete one account
        db_with_transactions.client.query(
            """
            delete Account
            filter .name = "Account 0"
            """
        )

        # THEN the account and its transactions are deleted
        assert len(db_with_transactions.client.query("select Account")) == 1
        assert len(db_with_transactions.client.query("select Transaction")) == 8
        # AND the other account is not
        assert (
            len(
                db_with_transactions.client.query(
                    "select Account filter .name = 'Account 1'"
                )
            )
            == 1
        )


class TestCounterparty:
    def test_upsert_counterparty_insert_1(self, empty_db):
        # GIVEN an empty database
        # WHEN I add a counterparty
        counterparty_uuid = uuid.uuid4()
        counterparty = Counterparty(
            uuid=counterparty_uuid, name="DUMMY", displayname="DUMMY"
        )
        upsert_counterparty(empty_db, counterparty)

        # THEN the counterparty is added
        counterparty = empty_db.client.query(
            """
            Select Counterparty {name} filter .uuid = <uuid>$uuid""",
            uuid=counterparty_uuid,
        )

        assert counterparty[0].name == "DUMMY"

    def test_upsert_counterparty_update_1(self, empty_db):
        # GIVEN a database with a counterparty
        counterparty_uuid = uuid.uuid4()
        counterparty = Counterparty(
            uuid=counterparty_uuid, name="DUMMY", displayname="DUMMY"
        )
        upsert_counterparty(empty_db, counterparty)

        # WHEN I modify the counterparty name
        updated_counterparty = Counterparty(
            uuid=counterparty_uuid, name="DUMMY MODIFIED", displayname="DUMMY MODIFIED"
        )
        upsert_counterparty(empty_db, updated_counterparty)

        # THEN the counterparty is updated
        counterparty = empty_db.client.query(
            """
            Select Counterparty {name} filter .uuid = <uuid>$uuid""",
            uuid=counterparty_uuid,
        )

        assert counterparty[0].name == "DUMMY MODIFIED"


class TestTransaction:
    def test_insert_transactions(self, db_2_accounts):
        # GIVEN a db with a 2 accounts
        # WHEN I add transactions to the accounts
        account_uuids = db_2_accounts.client.query("select Account.uuid")
        for account_uuid in account_uuids:
            for i in range(2):
                insert_transaction(db_2_accounts, account_uuid)

        # THEN the transactions are added
        assert len(db_2_accounts.client.query("select Transaction")) == 4
        # AND are linked to an account
        t_0 = db_2_accounts.client.query("select Transaction { account: {uuid}}")[0]
        assert isinstance(t_0.account.uuid, uuid.UUID)
