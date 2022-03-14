# schemas.py
#
# Starling Bank schema definitions

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

# = ACCOUNTS ==========================================================================================================
from starling_server.server.schemas.account import AccountSchema


class StarlingAccountSchema(BaseModel):
    """Represents a Starling Bank account."""

    accountUid: uuid.UUID
    name: str
    accountType: str
    currency: str
    createdAt: datetime
    defaultCategory: uuid.UUID  # FIXME UUID and -> uuid

    @staticmethod
    def to_server_accountschema(account: "StarlingAccountSchema") -> AccountSchema:
        return AccountSchema(
            uuid=account.accountUid,
            # bank_name=bank_name,
            account_name=account.name,
            currency=account.currency,
            created_at=account.createdAt,
        )


class StarlingAccountsSchema(BaseModel):
    accounts: List[StarlingAccountSchema]


class StarlingMainAccountsSchema(BaseModel):
    type_name: str
    accounts: List[StarlingAccountSchema]


class StarlingSignedCurrencyAndAmountSchema(BaseModel):
    currency: str
    minorUnits: int


class StarlingBalanceSchema(BaseModel):
    clearedBalance: StarlingSignedCurrencyAndAmountSchema
    pendingTransactions: StarlingSignedCurrencyAndAmountSchema
    effectiveBalance: StarlingSignedCurrencyAndAmountSchema


# = TRANSACTIONS  ======================================================================================================


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
