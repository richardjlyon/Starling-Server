# account.py
#
# Server account schema definitions.

from pydantic import BaseModel

from providers.starling.schemas import StarlingBalanceSchema


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
