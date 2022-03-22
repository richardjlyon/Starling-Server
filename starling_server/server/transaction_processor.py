"""
The transaction processor is called by the route dispatcher. It computes transaction display names and categories based on configuration tables.
"""
from typing import Optional

from starling_server.server.schemas.transaction import TransactionSchema


class TransactionProcessor:
    """A class for setting transaction display names and categories."""

    def __init__(self, db):
        self.db = db

    def upsert_display_name(self, name: str, display_name: str) -> None:
        """
        Insert the name / display_name pair in NameDisplayname database table.
        Args:
            name (str): the name to insert
            display_name (str): the display_name to insert

        """
        self.db.upsert_display_name(name, display_name)

    def display_name_for_name(self, name) -> Optional[str]:
        """
        Return the display name from NameDisplayname database table for the given name.
        Args:
            name (str):the name to match

        Returns: The display name, or None

        """
        results = self.db.display_name_for_name(name)
        if len(results) > 0:
            return results[0].display_name

    def delete_name(self, name: str):
        """
        Delete the name / display_name pair from NameDisplayname database table.
        Args:
            name (str): the name to match

        """
        self.db.delete_name(name)

    def assign_display_name(self, transaction: TransactionSchema) -> TransactionSchema:
        new_transaction = transaction
        new_transaction.counterparty.display_name = transaction.counterparty.name
        return new_transaction

    def assign_category(self, transaction: TransactionSchema):
        pass
