# api.py
#
# Defines an abstract API base class

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from server.schemas.account import AccountSchema, AccountBalanceSchema
from server.schemas.transaction import TransactionSchema


class BaseAPI(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_accounts(self) -> List[AccountSchema]:
        """Get the accounts held at the bank."""
        pass

    @abstractmethod
    def get_account_balance(self, account_uuid: str) -> List[AccountBalanceSchema]:
        """Get the balances of the account with the given id."""
        pass

    @abstractmethod
    def get_transactions_between(
        self, account_uuid: str, start_date: datetime, end_date: datetime
    ) -> List[TransactionSchema]:
        """Get the transactions for the account with the given id between the given dates."""
        pass
