# transaction.py
#
# Server transaction schema definitions.

import re
from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel

from src.providers.starling.schemas import StarlingTransactionSchema


class TransactionSchema(BaseModel):
    """Defines the server transaction response model."""

    uuid: str
    account_uuid: str
    time: datetime
    counterparty_name: str
    amount: float
    reference: Optional[str]

    @staticmethod
    def from_StarlingTransactionSchema(
            t: StarlingTransactionSchema,
    ) -> "TransactionSchema":
        return TransactionSchema(
            uuid=t.feedItemUid,
            time=t.transactionTime,
            counterparty_name=t.counterPartyName,
            amount=t.sourceAmount.compute_amount(t.direction),
            reference=clean_string(t.reference),
        )


def clean_string(the_string: Optional[str]) -> Optional[str]:
    """Replace multiple spaces with a single space."""
    if the_string:
        return str(re.sub(" +", " ", the_string).strip())
    else:
        return None
