# tests/conftest.py
#
# provides general test fixtures and utilities

import pathlib
import uuid
from typing import List

import pytest

from starling_server.db.edgedb.database import Database
from starling_server.providers.starling.account_helper import AccountHelper
from starling_server.server.route_dispatcher import RouteDispatcher
from starling_server.server.secrets import token_filepath

testdb = Database(database="test")

TEST_FOLDER = pathlib.Path(__file__).parent.absolute()

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


@pytest.fixture()
def personal_account_bank_name():
    """Provides the id for the personal account."""
    return personal_account["bank_name"]


@pytest.fixture()
def personal_account_id():
    """Provides the id for the personal account."""
    return uuid.UUID(personal_account["account_uuid"])


@pytest.fixture()
def personal_auth_token():
    """Provides the auth token for the personal account from the file system."""
    with open(token_filepath, "r") as f:
        return f.read().strip()


@pytest.fixture
def empty_db():
    """Returns an empty test database, and destroys its contents after testing."""
    reset()
    yield testdb
    # reset() # FIXME allows the database to be inspected - uncomment this when done


@pytest.fixture()
def live_helper():
    """Provides an initialised account helper object."""
    helper = AccountHelper()
    helper.initialise()  # ensure it has account data # FIXME this test side effect acts on live data
    return helper


@pytest.fixture()
def empty_dispatcher(empty_db, live_helper):
    """Provides a dispatcher with no banks or accounts and a live helper."""
    return RouteDispatcher(database=empty_db, account_helper=live_helper)


@pytest.mark.asyncio
@pytest.fixture()
async def live_dispatcher(empty_db, live_helper):
    """Provides a dispatcher with banks and accounts populated and a live helper."""
    dispatcher = RouteDispatcher(database=empty_db, account_helper=live_helper)
    await dispatcher.update_banks_and_accounts()
    return dispatcher


# = DATABASE UTILITY QUERIES =========================================================================================


def reset():
    testdb.client.query(
        """
        delete Transaction;
        """
    )
    testdb.client.query(
        """
        delete Account;
        """
    )
    testdb.client.query(
        """
        delete Bank;
        """
    )
    testdb.client.close()


def select_accounts():
    accounts = testdb.client.query(
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
    testdb.client.close()
    return accounts


def select_transactions():
    transactions = testdb.client.query(
        """
        select Transaction {
            account: { uuid, name },
            uuid,
            time,
            counterparty_name,
            amount,
            reference
        };
        """
    )
    testdb.client.close()
    return transactions


def show(things: List, message=None) -> None:
    print()
    if message is not None:
        print(f"\n{message}\n===========================:")
    for thing in things:
        print(thing)
