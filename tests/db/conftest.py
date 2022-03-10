import uuid
from datetime import datetime
from random import random
from typing import List

import pytest
import pytz

from starling_server.db.edgedb.database import Database
from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema

testdb = Database(database="test")


@pytest.fixture
def db():
    reset()
    yield testdb
    # reset()


def insert_2_accounts(thedb) -> None:
    """A database with two accounts, no transactions."""
    accounts = make_accounts(2)
    for account in accounts:
        thedb.insert_or_update_account(account)


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


def make_accounts(number) -> List[AccountSchema]:
    return [
        AccountSchema(
            uuid=str(uuid.uuid4()),
            bank_name=f"Starling Personal {i}",
            account_name=f"Account {i}",
            currency="GBP",
            created_at=datetime.now(pytz.timezone("Europe/London")),
        )
        for i in range(number)
    ]


def make_transactions(number: int, account_uuid: str) -> List[TransactionSchema]:
    return [
        TransactionSchema(
            uuid=str(uuid.uuid4()),
            account_uuid=str(account_uuid),
            time=datetime.now(pytz.timezone("Europe/London")),
            counterparty_name=f"Counterparty {i}",
            amount=random() * 10000,
            reference=f"{str(account_uuid)[-4:]}/{i}",
        )
        for i in range(number)
    ]
