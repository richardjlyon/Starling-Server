# db/db_base.py
#
# Defines a base class for a database provider
from abc import ABC, abstractmethod


class DBBase(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def reset(self):
        pass

    # BANKS ==========================================================================================================

    @abstractmethod
    def bank_upsert(self, bank_name):
        pass

    @abstractmethod
    def bank_delete(self, bank_name):
        pass

    # ACCOUNTS ========================================================================================================

    @abstractmethod
    def account_upsert(self, token, account):
        pass

    @abstractmethod
    def accounts_select(self):
        pass

    @abstractmethod
    def account_select_for_uuid(self, account_uuid):
        pass

    @abstractmethod
    def account_delete(self, account_uuid):
        pass

    # TRANSACTIONS ===================================================================================================

    @abstractmethod
    def transaction_upsert(self, transaction):
        pass

    @abstractmethod
    def transactions_select_for_account_uuid(self, account_uuid, offset, limit):
        pass

    @abstractmethod
    def transactions_select_between(self, start_date, end_date):
        pass

    @abstractmethod
    def transactions_delete_for_account_uuid(self, account_uuid):
        pass

    # COUNTERPARTIES ==========================================================

    @abstractmethod
    def counterparty_upsert(self, counterparty):
        pass

    # DISPLAY NAMES ================================================================================================

    @abstractmethod
    def display_name_map_upsert(self, name, displayname):
        pass

    @abstractmethod
    def display_name_map_delete(self, name):
        pass

    @abstractmethod
    def display_name_map_select(self):
        pass

    # CATEGORIES ======================================================================================================

    @abstractmethod
    def categorygroup_upsert(self, category):
        pass

    @abstractmethod
    def category_upsert(self, category):
        pass

    @abstractmethod
    def category_delete(self, category):
        pass

    @abstractmethod
    def categorygroup_delete(self, group_name):
        pass

    @abstractmethod
    def categories_select(self):
        pass

    @abstractmethod
    def categorymap_upsert(self, name_category):
        pass

    @abstractmethod
    def categorymap_select_all(self):
        pass
