# api.py
#
# Defines an abstract API base class

from abc import ABC, abstractmethod
from typing import List

from server.schemas.account import AccountSchema, AccountBalanceSchema


class BaseAPI(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_accounts(self) -> List[AccountSchema]:
        pass

    @abstractmethod
    def get_account_balance(self, account_uuid: str) -> List[AccountBalanceSchema]:
        pass

    @abstractmethod
    def to_server_account_schema(self, account):  # FIXME - type?
        pass

    @abstractmethod
    def to_server_account_balance_schema(
        self, account_uuid, balance
    ) -> AccountBalanceSchema:  # FIXME - type?
        pass
