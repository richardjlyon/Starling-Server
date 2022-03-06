# api.py
#
# Defines an abstract API base class

from abc import ABC, abstractmethod
from typing import List

from server.schemas.account import AccountSchema


class BaseAPI(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_accounts(self) -> List[AccountSchema]:
        pass

    @abstractmethod
    def get_account_balances(self):
        pass

    @abstractmethod
    def to_server_account_schema(self, account):  # FIXME - type?
        pass
