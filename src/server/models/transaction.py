import re
from datetime import datetime
from typing import Optional, List

from pydantic.main import BaseModel


class SourceAmount(BaseModel):
    """Currency dcit"""

    currency: str
    minorUnits: int

    def compute_amount(self, direction: str) -> float:
        """Compute a transaction amount in pounds. Outflow is negative."""
        if direction == "OUT":
            sign = -1
        else:
            sign = 1

        return sign * self.minorUnits / 100.0


class StarlingTransactionSchema(BaseModel):
    """Represents a Starling Bank transaction."""

    feedItemUid: str
    transactionTime: datetime
    counterPartyUid: str
    counterPartyName: str
    counterPartyType: str
    direction: str
    sourceAmount: SourceAmount
    reference: Optional[str] = None
    status: str


class StarlingTransactionsSchema(BaseModel):
    feedItems: List[StarlingTransactionSchema]


class TransactionSchema(BaseModel):
    """Defines the server transaction response model."""

    uuid: str
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
