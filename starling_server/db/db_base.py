# db/db_base.py
#
# Defines a base class for a database provider
import uuid
from abc import ABC, abstractmethod
from typing import List

from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema


class DBBase(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def reset(self, accounts: List[AccountSchema]):
        pass

    @abstractmethod
    def insert_or_update_account(self, bank_name: str, account: AccountSchema):
        pass

    @abstractmethod
    def get_accounts(self, as_schema: bool = False) -> List[AccountSchema]:
        pass

    @abstractmethod
    def insert_or_update_transaction(self, transaction: TransactionSchema):
        pass

    @abstractmethod
    def get_transactions_for_account(self, account_uuid: uuid.UUID):
        pass

    @abstractmethod
    def get_last_transaction_date_for_account(self, account_id: uuid.UUID):
        pass
