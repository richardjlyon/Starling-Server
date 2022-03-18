import uuid
from datetime import datetime

from starling_server.server.schemas.transaction import (
    TransactionSchema,
    Counterparty,
    clean_string,
)


def test_transaction_schema():
    t = TransactionSchema(
        uuid=uuid.uuid4(),
        account_uuid=uuid.uuid4(),
        time=datetime.now(),
        counterparty=Counterparty(uuid=uuid.uuid4(), name="TEST COUNTERPARTY"),
        amount=1.23,
        reference="the reference",
    )
    assert isinstance(t, TransactionSchema)


def test_clean_string():
    bad_reference = "A string       with bad spacing     "
    good_reference = "A string with bad spacing"
    assert clean_string(bad_reference) == good_reference
