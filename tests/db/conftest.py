# db/conftest.py
#
# fixtures for testing a database instance with dummy data

import uuid
from datetime import datetime
from random import random
from typing import List

import pytest
import pytz

from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema


@pytest.fixture
def db_with_two_accounts(empty_db):
    """Make a clean database with two test accounts."""
    db = empty_db
    accounts = make_accounts(2)
    for account in accounts:
        db.insert_or_update_account(account)

    return db


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
            counterparty_name=f"Counterparty {i}",
            amount=random() * 10000,
            reference=f"{str(account_uuid)[-4:]}/{i}",
        )
        for i in range(number)
    ]
