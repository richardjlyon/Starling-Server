# server/schemas/account.py
#
# Server account schema definitions.

from datetime import datetime

from pydantic import BaseModel, UUID4


class AccountSchema(BaseModel):
    """Defines the server account schema."""

    uuid: UUID4
    bank_name: str
    account_name: str
    currency: str
    created_at: datetime


class AccountBalanceSchema(BaseModel):
    """Defines the server account balance schema."""

    uuid: UUID4
    cleared_balance: float
    pending_transactions: float
    effective_balance: float
