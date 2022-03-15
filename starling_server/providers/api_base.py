# api_base.py
#
# Defines an abstract API base class
import uuid
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
        pass

    @abstractmethod
    async def get_account_balance(
        self, account_uuid: str
    ) -> Coroutine[Any, Any, AccountBalanceSchema]:
        """Get the balances of the account with the given id."""
        pass

    @abstractmethod
    async def get_transactions_for_account_id_between(
        self,
        account_uuid: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Coroutine[Any, Any, List[TransactionSchema]]:
        """Get the transactions for the account with the given id between the given dates."""
        pass


class BaseAPIV2(ABC):
    def __init__(self, auth_token: str, account_uuid: uuid.UUID):
        super().__init__()
        self.token = auth_token
        self.account_uuid = account_uuid

    @abstractmethod
    def get_accounts(self) -> list[AccountSchema]:
        pass

    @abstractmethod
    def get_account_balance(self) -> AccountBalanceSchema:
        pass

    @abstractmethod
    def get_transactions_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[TransactionSchema]:
        pass
