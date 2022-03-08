# db_base.py
#
# Defines a base class for a database provider
from abc import ABC, abstractmethod

from src.server.schemas.account import AccountSchema


class DBBase(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def save_account(self, account: AccountSchema):
        """Save or upadte account to the database."""
        pass
