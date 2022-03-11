import uuid
from datetime import datetime

from starling_server.server.schemas.transaction import TransactionSchema, clean_string


def test_transaction_schema():
    s = TransactionSchema(
        uuid=str(uuid.uuid4()),
        account_uuid=str(uuid.uuid4()),
        time=datetime.now(),
        counterparty_name="payee",
        amount=1.23,
        reference="the reference",
    )

    assert isinstance(s, TransactionSchema)


def test_clean_string():
    bad_reference = "A string       with bad spacing     "
    good_reference = "A string with bad spacing"
    assert clean_string(bad_reference) == good_reference
