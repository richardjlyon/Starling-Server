# tests/conftest.py
#
# provides general test fixtures and utilities
import json
import pathlib
import uuid
from dataclasses import dataclass
from typing import List

import pytest
from pydantic import parse_obj_as, PydanticTypeError

from starling_server.cli.commands.account.account_add import initialise_bank
from starling_server.db.edgedb.database import Database
from starling_server.providers.starling.schemas import (
    StarlingTransactionsSchema,
    StarlingTransactionSchema,
)
from starling_server.server.route_dispatcher import RouteDispatcher
from starling_server.server.schemas.transaction import TransactionSchema
from starling_server.server.transaction_processor import TransactionProcessor
from tests.db.database.conftest import reset
from .secrets import token_filepath

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
    """Returns a test database populated with live accounts (no transactions)."""
    await initialise_bank(empty_db, bank_name=config.bank_name, token=config.token)
    return empty_db


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


def show(things: List, message=None) -> None:
    print()
    if message is not None:
        print(f"\n{message}\n===========================:")
    for thing in things:
        print(thing)


# = Transaction Processor fixtures ===================================================================================


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
