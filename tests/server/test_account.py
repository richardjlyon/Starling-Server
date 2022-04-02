import uuid
from datetime import datetime

from starling_server.providers.starling.api import StarlingProvider
from starling_server.server.handlers.account import Account
from starling_server.server.schemas import AccountSchema

test_schema = AccountSchema(
    uuid=uuid.UUID("5b692051-b699-40f8-a48b-d14d554a9bd1"),
    bank_name="Starling Personal",
    account_name="Personal",
    currency="GBP",
    created_at=datetime.now(),
)


def test_init():
    account = Account(schema=test_schema)
    assert isinstance(account.provider, StarlingProvider)
