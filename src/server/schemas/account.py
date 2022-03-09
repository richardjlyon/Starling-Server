# account.py
#
# Server account schema definitions.
from datetime import datetime

from pydantic import BaseModel


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
