# transaction.py
#
# Server transaction schema definitions.

import re
from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel


class TransactionSchema(BaseModel):
    """Defines the server transaction response model."""

    uuid: str
    account_uuid: str
    time: datetime
    counterparty_name: str
    amount: float
    reference: Optional[str]


def clean_string(the_string: Optional[str]) -> Optional[str]:
    """Replace multiple spaces with a single space."""
    if the_string:
        return str(re.sub(" +", " ", the_string).strip())
    else:
        return None
