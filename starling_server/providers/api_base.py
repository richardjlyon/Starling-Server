# api.py
#
# Defines an abstract API base class

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Coroutine, Any

from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema


class BaseAPI(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    async def get_accounts(self) -> Coroutine[Any, Any, List[AccountSchema]]:
        """Get the accounts held at the bank."""
        pass

    @abstractmethod
    async def get_account_balance(
        self, account_uuid: str
    ) -> Coroutine[Any, Any, AccountBalanceSchema]:
        """Get the balances of the account with the given id."""
        pass

    @abstractmethod
    async def get_transactions_between(
        self, account_uuid: str, start_date: datetime, end_date: datetime
    ) -> Coroutine[Any, Any, List[TransactionSchema]]:
        """Get the transactions for the account with the given id between the given dates."""
        pass
