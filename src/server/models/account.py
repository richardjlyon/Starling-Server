from datetime import datetime
from typing import List

from pydantic import BaseModel


# = STARLING SCHEMAS ================================================================================================


class StarlingAccountSchema(BaseModel):
    """Represents a Starling Bank account."""

    accountUid: str
    name: str
    accountType: str
    currency: str
    createdAt: datetime
    defaultCategory: str


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


# = SERVER SCHEMAS ================================================================================================


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
