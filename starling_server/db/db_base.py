# db/db_base.py
#
# Defines a base class for a database provider
import uuid
from abc import ABC, abstractmethod
from typing import List

from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema, Counterparty


class DBBase(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def upsert_bank(self, bank_name: str, token: str):
        pass

    @abstractmethod
    def delete_bank(self, bank_name: str):
        pass

    @abstractmethod
    def upsert_display_name(self, name: str, display_name: str):
        pass

    @abstractmethod
    def display_name_for_name(self, name: str) -> str:
        pass

    @abstractmethod
    def delete_name(self, name: str):
        pass

    @abstractmethod
    def insert_category_group(self, group_name: str):
        pass

    @abstractmethod
    def upsert_category(self, group_name: str, category_name: str):
        pass

    @abstractmethod
    def upsert_account(self, token: str, account: AccountSchema):
        pass

    @abstractmethod
    def select_accounts(self, as_schema: bool = False) -> List[AccountSchema]:
        pass

    @abstractmethod
    def select_account_for_account_uuid(
        self, account_uuid: uuid.UUID, as_schema: bool = False
    ) -> List[AccountSchema]:
        pass

    @abstractmethod
    def delete_account(self, account_uuid: uuid.UUID):
        pass

    @abstractmethod
    def upsert_counterparty(self, counterparty: Counterparty):
        pass

    @abstractmethod
    def upsert_transaction(self, transaction: TransactionSchema):
        pass

    @abstractmethod
    def select_transactions_for_account(self, account_uuid: uuid.UUID):
        pass

    @abstractmethod
    def delete_transactions_for_account_id(self, account_uuid: uuid.UUID):
        pass

    @abstractmethod
    def reset(self):
        pass
