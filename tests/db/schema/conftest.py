import uuid
from datetime import datetime
from random import random, choice

import edgedb
import pytest
import pytz

client = edgedb.create_client(database="test")
test_bank_name = "Starling Personal"


@pytest.fixture
def db():
    """Returns an empty test database, and destroys its contents after testing."""
    reset()
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


def reset():
    client.query(
        """
        delete Transaction;
        """
    )
    client.query(
        """
        delete Account;
        """
    )
    client.query(
        """
        delete Bank;
        """
    )
    client.query(
        """
        delete Category;
        """
    )
    client.query(
        """
        delete CategoryGroup;
        """
    )
    client.close()


def insert_bank(db, name):
    db.query(
        """
        insert Bank {
            name := <str>$name,
            auth_token_hash := "dummy token"
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
                    category_group := category_group
                }
                """,
                group=group,
                category=category,
            )
            category_list.append(category)

    return category_list


def insert_transaction(db, account_uuid):
    transaction_uuid = uuid.uuid4()
    db.query(
        """
        with 
            account := (select Account filter .uuid = <uuid>$account_uuid),
            category := (select Category filter .name = <str>$category)
        insert Transaction {
            account := account,
            category := category,
            uuid := <uuid>$transaction_uuid,
            time := <datetime>$now,
            counterparty_name := "DUMMY COUNTERPARTY",
            amount := <float32>$amount,
            reference := <str>$reference,
        }
        """,
        account_uuid=account_uuid,
        category=make_category(db),
        transaction_uuid=transaction_uuid,
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
