import uuid
from datetime import datetime
from random import random, choice

import edgedb
import pytest
import pytz

from starling_server.server.schemas.transaction import Counterparty
from tests.db.database.conftest import reset

client = edgedb.create_client(database="test")
test_bank_name = "Starling Personal"


@pytest.fixture
def db():
    """Returns an empty test database, and destroys its contents after testing."""
    reset(client)
    yield client
    # reset() # FIXME allows the database to be inspected - uncomment this when done


@pytest.fixture
def db_with_accounts(db):
    insert_bank(db, test_bank_name)
    insert_categories(db)
    for account_name in ["Personal Account 1", "Personal Account 2"]:
        insert_account(db, account_name)
    return db


@pytest.fixture
def db_with_transactions(db_with_accounts):
    """Returns a database with 1 bank, 2 accounts, 2 transactions in each with categories."""
    account_uuids = db_with_accounts.query("select Account.uuid")
    for account_uuid in account_uuids:
        for i in range(2):
            insert_transaction(db_with_accounts, account_uuid)

    return db_with_accounts


# = Helpers


def insert_bank(db, name):
    db.query(
        """
        insert Bank {
            name := <str>$name,
        }
        """,
        name=name,
    )


def insert_account(db, name):
    account_uuid = uuid.uuid4()
    db.query(
        """
        with bank := (select Bank filter .name = <str>$bank_name)
        insert Account {
            bank := bank,
            uuid := <uuid>$uuid,
            name := <str>$name,
            currency := "GBP",
            created_at := <datetime>$now,
        }
        """,
        bank_name=test_bank_name,
        uuid=account_uuid,
        name=name,
        now=datetime.now(pytz.timezone("Europe/London")),
    )


def insert_categories(db):
    data = {
        "Mandatory": ["Energy", "Food", "Insurance"],
        "Discretionary": ["Entertainment", "Hobbies", "Vacation"],
    }

    category_list = []

    for group, categories in data.items():

        db.query(
            """
            insert CategoryGroup { name := <str>$group }
            """,
            group=group,
        )

        for category in categories:
            db.query(
                """
                with category_group := (select CategoryGroup filter .name = <str>$group)
                insert Category {
                    name := <str>$category,
                    category_group := category_group,
                    uuid := <uuid>$uuid
                }
                """,
                group=group,
                category=category,
                uuid=uuid.uuid4(),
            )
            category_list.append(category)

    return category_list


def upsert_counterparty(db, counterparty: Counterparty):
    db.query(
        """
        insert Counterparty {
            uuid := <uuid>$uuid,
            name := <str>$name,
            display_name := <str>$display_name
        } unless conflict on .uuid else (
            update Counterparty
            set {
                name := <str>$name,
                display_name := <str>$display_name
            }
        )
        """,
        uuid=counterparty.uuid,
        name=counterparty.name,
        display_name=counterparty.display_name,
    )


def insert_transaction(db, account_uuid):
    counterparty_uuid = uuid.uuid4()
    counterparty = Counterparty(
        uuid=counterparty_uuid, name="DUMMY", display_name="DUMMY"
    )
    upsert_counterparty(db, counterparty)
    db.query(
        """
        with 
            account := (select Account filter .uuid = <uuid>$account_uuid),
            category := (select Category filter .name = <str>$category),
            counterparty := (select Counterparty filter .uuid = <uuid>$counterparty_uuid),
        insert Transaction {
            account := account,
            category := category,
            uuid := <uuid>$transaction_uuid,
            time := <datetime>$now,
            counterparty := counterparty,
            amount := <float32>$amount,
            reference := <str>$reference,
        }
        """,
        account_uuid=account_uuid,
        category=make_category(db),
        counterparty_uuid=counterparty_uuid,
        transaction_uuid=uuid.uuid4(),
        now=datetime.now(pytz.timezone("Europe/London")),
        amount=random() * 100,
        reference=f"Ref: {str(account_uuid)[-4:]}",
    )


def make_category(db):
    categories = list(db.query("select Category.name"))
    if len(categories) == 0:
        return ""
    else:
        return choice(categories)
