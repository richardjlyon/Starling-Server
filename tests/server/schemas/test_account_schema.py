import uuid
from datetime import datetime

from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema


def test_account_schema():
    s = AccountSchema(
        uuid=str(uuid.uuid4()),
        bank_name="Starling Personal",
        account_name="Personal",
        currency="GBP",
        created_at=datetime.now(),
    )

    assert isinstance(s, AccountSchema)


def test_account_balance_schema():
    s = AccountBalanceSchema(
        uuid=uuid.uuid4(),
        cleared_balance=1.0,
        pending_transactions=1.0,
        effective_balance=1.0,
    )

    assert isinstance(s, AccountBalanceSchema)
