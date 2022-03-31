# db/db_base.py
#
# Defines a base class for a database provider
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema, Counterparty


class DBBase(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def reset(self):
        pass

    # BANKS ==========================================================================================================

    @abstractmethod
    def upsert_bank(self, bank_name: str) -> None:
        pass

    @abstractmethod
    def delete_bank(self, bank_name: str) -> None:
        pass

    # ACCOUNTS ========================================================================================================

    @abstractmethod
    def upsert_account(self, token: str, account: AccountSchema) -> None:
        pass

    @abstractmethod
    def select_accounts(self) -> Optional[List[AccountSchema]]:
        pass

    @abstractmethod
    def select_account_for_account_uuid(
        self, account_uuid: uuid.UUID
    ) -> Optional[AccountSchema]:
        pass

    @abstractmethod
    def delete_account(self, account_uuid: uuid.UUID) -> None:
        pass

    # TRANSACTIONS ===================================================================================================

    @abstractmethod
    def upsert_transaction(self, transaction: TransactionSchema) -> None:
        pass

    @abstractmethod
    def select_transactions_for_account(
        self, account_uuid: uuid.UUID, offset: int, limit: int
    ) -> Optional[List[TransactionSchema]]:
        pass

    @abstractmethod
    def select_transactions_between(
        self, start_date: datetime, end_date: datetime
    ) -> Optional[List[TransactionSchema]]:
        pass

    @abstractmethod
    def delete_transactions_for_account_id(self, account_uuid: uuid.UUID) -> None:
        pass

    # COUNTERPARTIES ================================================================================================

    @abstractmethod
    def upsert_counterparty(self, counterparty: Counterparty) -> None:
        pass

    @abstractmethod
    def display_name_map_upsert(
        self, fragment: str = None, display_name: str = None
    ) -> None:
        pass

    @abstractmethod
    def display_name_map_delete(self, fragment: str) -> None:
        pass

    @abstractmethod
    def display_name_map_select(self) -> Optional[set]:
        pass

    # CATEGORIES ======================================================================================================

    @abstractmethod
    def insert_category_group(self, group_name: str):
        pass

    @abstractmethod
    def upsert_category(self, group_name: str, category_name: str):
        pass
