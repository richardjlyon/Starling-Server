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
from tests.conftest import select_accounts


@pytest.fixture
def db_with_two_accounts(empty_db, config):
    """Make a clean database with two test accounts."""
    db = empty_db
    accounts = make_accounts(2)
    for account in accounts:
        db.insert_or_update_account(config.token, account)

    return db


@pytest.fixture
def db_with_four_transactions(empty_db, config):
    """Make a clean database with two accounts of two transactions each."""
    accounts = make_accounts(2)
    for account in accounts:
        empty_db.insert_or_update_account(config.token, account)

    accounts_db = select_accounts()
    for account_db in accounts_db:
        transactions = make_transactions(2, account_uuid=account_db.uuid)
        for transaction in transactions:
            empty_db.insert_or_update_transaction(transaction)

    return empty_db


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
