# tests/conftest.py
#
# provides general test fixtures and utilities
import json
import pathlib
import uuid
from dataclasses import dataclass
from datetime import datetime
from random import random, choice
from typing import List

import pytest
import pytz
from pydantic import parse_obj_as, PydanticTypeError

from starling_server import cfg
from starling_server.db.edgedb.database import Database
from starling_server.providers.starling.schemas import (
    StarlingTransactionsSchema,
    StarlingTransactionSchema,
)
from starling_server.server.account import Account, get_provider_class, get_auth_token
from starling_server.server.route_dispatcher import RouteDispatcher
from starling_server.server.schemas import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema, Counterparty
from starling_server.server.transaction_processor import TransactionProcessor
from .secrets import token_filepath

testdb = Database(database="test")

TEST_FOLDER = pathlib.Path(__file__).parent.absolute()

test_bank_name = "Starling Personal"

personal_account = {
    "bank_name": "Starling Personal",
    "account_uuid": "5b692051-b699-40f8-a48b-d14d554a9bd1",
    "default_category": "b23c9e8b-4377-4d9a-bce3-e7ee5477af50",
}

business_account = {
    "bank_name": "Starling Business",
    "account_uuid": "7327c655-31f6-4f21-ac8e-74880e5c8a47",
    "default_category": "8a489b6e-8d06-4e21-a122-e4e4ed3e2d84",
}


@dataclass
class Config:
    bank_name: str
    account_uuid: uuid.UUID
    token: str


@pytest.fixture()
def config():
    with open(token_filepath, "r") as f:
        token = f.read().strip()

    return Config(
        bank_name=personal_account["bank_name"],
        account_uuid=uuid.UUID(personal_account["account_uuid"]),
        token=token,
    )


# Database fixtures ==================================================================================================


@pytest.fixture
def empty_db():
    """Returns an empty test database, and destroys its contents after testing."""
    reset(testdb.client)
    yield testdb
    # reset() # FIXME allows the database to be inspected - uncomment this when done


@pytest.fixture
def db_2_accounts(empty_db, config):
    """Inserts two test accounts."""
    accounts = make_accounts(2)
    for account in accounts:
        empty_db.upsert_account(config.token, account)
    return empty_db


@pytest.fixture
def db_with_accounts(empty_db):
    insert_bank(empty_db, test_bank_name)
    insert_categories(empty_db)
    for account_name in ["Personal Account 1", "Personal Account 2"]:
        insert_account(empty_db, account_name)
    return empty_db


@pytest.fixture
@pytest.mark.asyncio
async def testdb_with_real_accounts(empty_db, config):
    """Returns a test database populated with live accounts (no transactions)."""

    await initialise_accounts(empty_db)
    return empty_db


@pytest.fixture
def db_4_transactions(db_2_accounts):
    """Inserts two accounts of two transactions each."""
    accounts_db = select_accounts(db_2_accounts)
    for account_db in accounts_db:
        transactions = make_transactions(2, account_uuid=account_db.uuid)
        for transaction in transactions:
            db_2_accounts.upsert_transaction(transaction)

    return db_2_accounts


@pytest.fixture
def db_with_transactions(db_with_accounts):
    """Returns a database with 1 bank, 2 accounts, 2 transactions in each with categories."""
    account_uuids = db_with_accounts.client.query("select Account.uuid")
    for account_uuid in account_uuids:
        for i in range(2):
            insert_transaction(db_with_accounts, account_uuid)

    return db_with_accounts.client


# RouteDispatcher fixtures ===========================================================================================


@pytest.fixture()
def empty_dispatcher(empty_db):
    """Provides a dispatcher with no banks or accounts and a live helper."""
    return RouteDispatcher(database=empty_db)


@pytest.fixture
def mock_transactions() -> List[TransactionSchema]:
    """Generate a list of transactions from a file to avoid an api call."""
    transaction_data_file = TEST_FOLDER / "test_data" / "transactions.json"
    with open(transaction_data_file, "r") as f:
        response = json.load(f)
    try:
        parsed_response = parse_obj_as(StarlingTransactionsSchema, response)
    except PydanticTypeError:
        raise RuntimeError(f"Pydantic type error")
    transactions_raw = parsed_response.feedItems
    account_uuid = uuid.uuid4()
    return [
        StarlingTransactionSchema.to_server_transaction_schema(
            account_uuid, transaction
        )
        for transaction in transactions_raw
    ]


# Transaction Processor fixtures ======================================================================================


@pytest.fixture()
def tp_empty(empty_db):
    """A transaction processor with an empty database"""
    return TransactionProcessor(empty_db)


@pytest.fixture()
def tp_two_pairs(tp_empty):
    """A transaction processor with a name pair"""
    name = "Riccarton Garden C"
    display_name = "Riccarton Garden Centre"

    tp_empty.upsert_display_name(name=name, display_name=display_name)

    name_fragment = "dwp"
    display_name = "Department of Work and Pensions"
    tp_empty.upsert_display_name(name_fragment=name_fragment, display_name=display_name)

    return tp_empty


# Route Dispatcher fixtures ===========================================================================================


@pytest.fixture()
def accounts(db_4_transactions):
    """Returns a list of accounts from the database"""
    return [
        Account(account_schema)
        for account_schema in testdb_with_real_accounts.select_accounts(as_schema=True)
    ]


# Helpers ==========================================================================================================


def reset(client):
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
    client.query(
        """
        delete Counterparty;
        """
    )
    client.query(
        """
        delete NameDisplayname;
        """
    )
    client.close()


def insert_bank(db, name):
    db.client.query(
        """
        insert Bank {
            name := <str>$name,
        }
        """,
        name=name,
    )


def select_banks(db):
    banks = db.client.query(
        """
        select Bank { name }
        """
    )
    db.client.close()
    return banks


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


@pytest.mark.asyncio
async def initialise_accounts(empty_db) -> None:
    """Initialise the test database with a bank and account."""
    bank_names = [bank["bank_name"] for bank in cfg.banks]
    for bank_name in bank_names:
        provider_class = get_provider_class(bank_name)
        auth_token = get_auth_token(bank_name)
        provider = provider_class(
            auth_token=auth_token, bank_name=bank_name, category_check=False
        )
        accounts = await provider.get_accounts()
        for account in accounts:
            empty_db.upsert_account(provider.auth_token, account)

    return empty_db


def insert_account(db, name):
    account_uuid = uuid.uuid4()
    db.client.query(
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


def make_transactions(number: int, account_uuid: uuid.UUID) -> List[TransactionSchema]:
    return [
        TransactionSchema(
            uuid=uuid.uuid4(),
            account_uuid=account_uuid,
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


def insert_transaction(db, account_uuid):
    counterparty_uuid = uuid.uuid4()
    counterparty = Counterparty(
        uuid=counterparty_uuid, name="DUMMY", display_name="DUMMY"
    )
    upsert_counterparty(db, counterparty)
    db.client.query(
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


def make_category(db):
    categories = list(db.client.query("select Category.name"))
    if len(categories) == 0:
        return ""
    else:
        return choice(categories)


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


# def insert_categories(db):
#     data = {
#         "Mandatory": ["Energy", "Food", "Insurance"],
#         "Discretionary": ["Entertainment", "Hobbies", "Vacation"],
#     }
#
#     category_list = []
#
#     for group, categories in data.items():
#
#         db.query(
#             """
#             insert CategoryGroup { name := <str>$group }
#             """,
#             group=group,
#         )
#
#         for category in categories:
#             db.query(
#                 """
#                 with category_group := (select CategoryGroup filter .name = <str>$group)
#                 insert Category {
#                     name := <str>$category,
#                     category_group := category_group,
#                     uuid := <uuid>$uuid
#                 }
#                 """,
#                 group=group,
#                 category=category,
#                 uuid=uuid.uuid4(),
#             )
#             category_list.append(category)
#
#     return category_list


def upsert_counterparty(db, counterparty: Counterparty):
    db.client.query(
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


def show(things: List, message=None) -> None:
    print()
    if message is not None:
        print(f"\n{message}\n===========================:")
    for thing in things:
        print(thing)
