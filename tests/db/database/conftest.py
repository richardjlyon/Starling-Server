# db/conftest.py
#
# fixtures for testing a database instance with dummy data

import uuid
from datetime import datetime
from random import random
from typing import List

import pytest
import pytz

from starling_server.db.edgedb.database import Database
from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema, Counterparty

test_bank_name = "Starling Business (TEST)"


@pytest.fixture
def db():
    """Returns an empty database and destroys its contents after testing."""
    test_db = Database(database="test")
    reset(test_db)
    # insert_categories(test_db)
    yield test_db
    # FIXME allows the database to be inspected - uncomment this when done
    # reset(test_db)


@pytest.fixture
def db_2_accounts(db, config):
    accounts = make_accounts(2)
    for account in accounts:
        db.upsert_account(config.token, account)
    return db


@pytest.fixture()
def counterparty(db):
    counterparty_uuid = uuid.uuid4()
    return Counterparty(uuid=counterparty_uuid, name="DUMMY", display_name="DUMMY")


@pytest.fixture
def db_4_transactions(empty_db):
    """Make a clean database with two accounts of two transactions each."""
    accounts = make_accounts(2)
    for account in accounts:
        empty_db.upsert_account("DUMMY TOKEN", account)

    accounts_db = select_accounts(empty_db)
    for account_db in accounts_db:
        transactions = make_transactions(2, account_uuid=account_db.uuid)
        for transaction in transactions:
            empty_db.upsert_transaction(transaction)

    return empty_db


def reset(db):
    db.client.query(
        """
        delete Transaction;
        """
    )
    db.client.query(
        """
        delete Account;
        """
    )
    db.client.query(
        """
        delete Bank;
        """
    )
    db.client.query(
        """
        delete Category;
        """
    )
    db.client.query(
        """
        delete CategoryGroup;
        """
    )
    db.client.query(
        """
        delete Counterparty;
        """
    )
    db.client.close()


def insert_categories(db) -> List[str]:
    data = {
        "Mandatory": ["Energy", "Food", "Insurance"],
        "Discretionary": ["Entertainment", "Hobbies", "Vacation"],
    }

    category_list = []

    for group_name, categories in data.items():
        db.insert_category_group(group_name)
        for category_name in categories:
            db.upsert_category(group_name, category_name)
            category_list.append(category_name)

    return category_list


def make_accounts(n) -> List[AccountSchema]:
    """Make n test accounts."""
    return [
        AccountSchema(
            uuid=uuid.uuid4(),
            bank_name=f"Starling Personal {i}",
            account_name=f"Account {i}",
            currency="GBP",
            created_at=datetime.now(pytz.timezone("Europe/London")),
        )
        for i in range(n)
    ]


def make_transactions(number: int, account_uuid: str) -> List[TransactionSchema]:
    return [
        TransactionSchema(
            uuid=str(uuid.uuid4()),
            account_uuid=str(account_uuid),
            time=datetime.now(pytz.timezone("Europe/London")),
            counterparty=Counterparty(
                uuid=uuid.uuid4(),
                name=f"Counterparty {i}",
                display_name=f"Counterparty Display {i}",
            ),
            amount=random() * 10000,
            reference=f"{str(account_uuid)[-4:]}/{i}",
        )
        for i in range(number)
    ]


def select_banks(db):
    banks = db.client.query(
        """
        select Bank { name }
        """
    )
    db.client.close()
    return banks


def select_accounts(db):
    accounts = db.client.query(
        """
        select Account {
            bank: { name },
            uuid,
            name,
            currency,
            created_at,
            transactions: { reference }
        };
        """
    )
    db.client.close()
    return accounts


def select_transactions(db):
    transactions = db.client.query(
        """
        select Transaction {
            account: { uuid, name },
            uuid,
            time,
            counterparty: {
                uuid, name, display_name
            },
            amount,
            reference
        };
        """
    )
    db.client.close()
    return transactions


# @pytest.fixture
# def db_with_two_accounts(empty_db):
#     """Make a clean database with two test accounts."""
#     db = empty_db
#     accounts = make_accounts(2)
#     for account in accounts:
#         db.upsert_account("DUMMY TOKEN", account)
#
#     return db
#
#
# @pytest.fixture
# def db_with_four_transactions(empty_db):
#     """Make a clean database with two accounts of two transactions each."""
#     accounts = make_accounts(2)
#     for account in accounts:
#         empty_db.upsert_account("DUMMY TOKEN", account)
#
#     accounts_db = select_accounts()
#     for account_db in accounts_db:
#         transactions = make_transactions(2, account_uuid=account_db.uuid)
#         for transaction in transactions:
#             empty_db.upsert_transaction(transaction)
#
#     return empty_db
