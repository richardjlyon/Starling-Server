# account.py
#
# Server account schema definitions.
from datetime import datetime

from pydantic import BaseModel

from providers.starling.schemas import StarlingBalanceSchema


class AccountSchema(BaseModel):
    """Defines the server account schema."""

    uuid: str
    bank_name: str
    account_name: str
    currency: str
    created_at: datetime


class AccountBalanceSchema(BaseModel):
    """Defines the server account balance schema."""

    account_uuid: str
    cleared_balance: float
    pending_transactions: float
    effective_balance: float

    @staticmethod
    def from_StarlingBalanceSchema(
        account_uuid: str, balance: StarlingBalanceSchema
    ) -> "AccountBalanceSchema":
        return AccountBalanceSchema(
            account_uuid=account_uuid,
            cleared_balance=balance.clearedBalance.minorUnits / 100.0,
            pending_transactions=balance.pendingTransactions.minorUnits / 100.0,
            effective_balance=balance.effectiveBalance.minorUnits / 100.0,
        )
