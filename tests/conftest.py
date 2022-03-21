# tests/conftest.py
#
# provides general test fixtures and utilities

import pathlib
import uuid
from dataclasses import dataclass
from typing import List

import pytest

from starling_server.db.edgedb.database import Database
from starling_server.server.config_helper import ConfigHelper
from starling_server.server.route_dispatcher import RouteDispatcher
from starling_server.server.secrets import token_filepath
from tests.db.database.conftest import reset

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


@pytest.fixture
def empty_db():
    """Returns an empty test database, and destroys its contents after testing."""
    reset(testdb.client)
    yield testdb
    # reset() # FIXME allows the database to be inspected - uncomment this when done


@pytest.fixture
@pytest.mark.asyncio
async def testdb_with_real_accounts(empty_db, config):
    """Returns a test database populated with live acounts (no transactions)."""
    config_helper = ConfigHelper(db=empty_db)
    await config_helper.initialise_bank(bank_name=config.bank_name, token=config.token)
    return empty_db


@pytest.fixture()
def empty_dispatcher(empty_db):
    """Provides a dispatcher with no banks or accounts and a live helper."""
    return RouteDispatcher(database=empty_db)


def show(things: List, message=None) -> None:
    print()
    if message is not None:
        print(f"\n{message}\n===========================:")
    for thing in things:
        print(thing)
