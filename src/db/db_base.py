# db_base.py
#
# Defines a base class for a database provider
from abc import ABC, abstractmethod

from server.schemas.transaction import TransactionSchema
from src.server.schemas.account import AccountSchema


class DBBase(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def insert_or_update_account(self, bank_name: str, account: AccountSchema):
        pass

    @abstractmethod
    def insert_or_update_transaction(self, transaction: TransactionSchema):
        pass
