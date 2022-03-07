# api.py
#
# Defines an abstract API base class

from abc import ABC, abstractmethod
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
    def get_transactions_for_account_id(
        self, account_uuid: str
    ) -> List[TransactionSchema]:
        """Get the transactions for the account with the given id.

        This function is expected to return transactions over a defined number of days up
        to the present time."""
        pass
