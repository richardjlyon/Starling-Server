# schemas.py
#
# Starling Bank schema definitions
import re
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

# = ACCOUNTS ==========================================================================================================
from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema


class StarlingAccountSchema(BaseModel):
    """Represents a Starling Bank account."""

    accountUid: uuid.UUID
    name: str
    accountType: str
    currency: str
    createdAt: datetime
    defaultCategory: uuid.UUID  # FIXME UUID and -> uuid

    @staticmethod
    def to_server_account_schema(
        bank_name: str, account: "StarlingAccountSchema"
    ) -> AccountSchema:
        return AccountSchema(
            uuid=account.accountUid,
            bank_name=bank_name,
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

    @staticmethod
    def to_server_account_balance_schema(
        account_uuid: uuid.UUID, balance: "StarlingBalanceSchema"
    ) -> AccountBalanceSchema:
        return AccountBalanceSchema(
            uuid=account_uuid,
            cleared_balance=balance.clearedBalance.minorUnits / 100.0,
            pending_transactions=balance.pendingTransactions.minorUnits / 100.0,
            effective_balance=balance.effectiveBalance.minorUnits / 100.0,
        )


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

    @staticmethod
    def to_server_transaction_schema(
        account_uuid: uuid.UUID, transaction: "StarlingTransactionSchema"
    ) -> TransactionSchema:
        def clean_string(the_string: Optional[str]) -> Optional[str]:
            """Replace multiple spaces with a single space."""
            if the_string:
                return str(re.sub(" +", " ", the_string).strip())
            else:
                return ""

        return TransactionSchema(
            uuid=uuid.UUID(transaction.feedItemUid),
            account_uuid=account_uuid,
            time=transaction.transactionTime,
            counterparty_name=transaction.counterPartyName,
            amount=transaction.sourceAmount.compute_amount(transaction.direction),
            reference=clean_string(transaction.reference),
        )


class StarlingTransactionsSchema(BaseModel):
    feedItems: List[StarlingTransactionSchema]
