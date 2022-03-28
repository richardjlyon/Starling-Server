"""
This module defines the base class for derived classes that access a provider's API scheme.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from starling_server.server.schemas import (
    AccountSchema,
    AccountBalanceSchema,
    TransactionSchema,
)


class Provider(ABC):
    def __init__(
        self,
        auth_token: str,
        bank_name: str,
        account_uuid: Optional[uuid.UUID],
        class_name: str,
    ):
        super().__init__()
        self._class_name = class_name
        self.auth_token = auth_token
        self.bank_name = bank_name
        self.account_uuid = account_uuid

    @abstractmethod
    def get_accounts(self) -> list[AccountSchema]:
        """Get the accounts associated with a bank."""

    @abstractmethod
    def get_account_balance(self) -> AccountBalanceSchema:
        """Get the balances of the account with the given id."""

    @abstractmethod
    def get_transactions_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[TransactionSchema]:
        """Get the transactions for the account with the given id between the given dates."""

    @property
    def class_name(self) -> str:
        """The class name of the instantiated object."""
        return self._class_name

    def __repr__(self):
        return f"<{self._class_name}>"
