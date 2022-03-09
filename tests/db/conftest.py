import uuid
from datetime import datetime
from random import random
from typing import List

import pytest
import pytz

from db.edgedb.database import Database
from server.schemas.account import AccountSchema

testdb = Database(database="test")


@pytest.fixture
def db():
    reset()
    yield testdb
    reset()


@pytest.fixture
def db_2_accounts(db):
    """A database with two accounts, no transactions."""
    accounts = make_accounts(2)
    for account in accounts:
        db.insert_or_update_account(account.bank_name, account)
    return accounts


def reset():
    testdb.client.query(
        """
        delete Account;
        """
    )
    testdb.client.query(
        """
        delete Transaction;
        """
    )
    testdb.client.close()


def select_accounts():
    accounts = testdb.client.query(
        """
        select Account {
            bank_name,
            account_name,
            transactions
        };
        """
    )
    testdb.client.close()
    return accounts


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


def make_transactions(account: int, total: int) -> List[dict]:
    return [
        {
            "uuid": uuid.uuid4(),
            "time": datetime.now(pytz.timezone("Europe/London")),
            "counterparty_name": f"Counterparty {i}",
            "amount": random() * 10000,
            "reference": f"Account {account} Transaction {i}",
        }
        for i in range(total)
    ]
