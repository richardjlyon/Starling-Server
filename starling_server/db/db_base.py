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
    def upsert_bank(self, bank_name):
        pass

    @abstractmethod
    def delete_bank(self, bank_name):
        pass

    # ACCOUNTS ========================================================================================================

    @abstractmethod
    def upsert_account(self, token, account):
        pass

    @abstractmethod
    def select_accounts(self):
        pass

    @abstractmethod
    def select_account_for_account_uuid(self, account_uuid):
        pass

    @abstractmethod
    def delete_account(self, account_uuid):
        pass

    # TRANSACTIONS ===================================================================================================

    @abstractmethod
    def upsert_transaction(self, transaction):
        pass

    @abstractmethod
    def select_transactions_for_account(self, account_uuid, offset, limit):
        pass

    @abstractmethod
    def select_transactions_between(self, start_date, end_date):
        pass

    @abstractmethod
    def delete_transactions_for_account_id(self, account_uuid):
        pass

    # COUNTERPARTIES ==========================================================

    @abstractmethod
    def upsert_counterparty(self, counterparty):
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
    def upsert_categorygroup(self, category):
        pass

    @abstractmethod
    def upsert_category(self, category):
        pass

    @abstractmethod
    def delete_category(self, category):
        pass

    @abstractmethod
    def delete_category_group(self, group_name):
        pass

    @abstractmethod
    def select_category_groups(self):
        pass

    @abstractmethod
    def select_categories(self):
        pass

    @abstractmethod
    def get_all_name_categories(self):
        pass

    @abstractmethod
    def upsert_name_category(self, name_category):
        pass
