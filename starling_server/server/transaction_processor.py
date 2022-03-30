"""
The transaction processor is called by the route dispatcher. It computes transaction display names and categories based
on configuration tables.
"""
from typing import Optional

from starling_server.db.edgedb.database import Database
from starling_server.server.schemas import TransactionSchema


class DisplaynameManager:
    """A class for managing entries in the DisplayNameMap table."""

    def __init__(self, db: Database):
        self.db = db

    def upsert_display_name(
        self, name: str = None, name_fragment: str = None, display_name: str = None
    ) -> None:
        """
        Insert the name / display_name pair in NameDisplayname database table.
        Args:
            name (str): the name to insert
            name_fragment (str): the name fragment to insert
            display_name (str): the display_name to insert

        """
        if display_name is None:
            raise ValueError("No display_name")

        if name is not None:
            self.db.upsert_display_name(name=name, display_name=display_name)
        elif name_fragment is not None:
            self.db.upsert_display_name(
                name_fragment=name_fragment, display_name=display_name
            )
        else:
            raise ValueError("name and display_name cannot both be None")

    def delete_name(self, name: str):
        """
        Delete the name / display_name pair from NameDisplayname database table.
        Args:
            name (str): the name to match

        """
        self.db.delete_name(name)


class CategoryManager:
    """A class for managing entries in the Category table."""

    def __init__(self, db: Database):
        self.db = db


class TransactionProcessor:
    """A class for setting transaction display names and categories."""

    def __init__(self, db: Database):
        self.db = db

    def display_name_for_name(self, name: str, fragment: bool = False) -> Optional[str]:
        """
        Return the display name from NameDisplayname database table for the given name.
        Args:
            name (str): the name to match
            fragment (bool): if true, search name fragments

        Returns: The display name, or None

        """
        if fragment:
            return self._get_display_name_for_matched_name(name)

        results = self.db.display_name_for_name(name)
        if len(results) > 0:
            return results[0].display_name

    def assign_category(self, transaction: TransactionSchema):
        pass

    def _get_display_name_for_matched_name(self, name: str) -> Optional[str]:
        """
        Match name to name_fragments and return display_name if one is found.
        Args:
            name (str): The name to match against fragments

        Returns: A display name, or None.

        """

        fragments = self.db.select_name_fragments()
        matches = [
            fragment.display_name
            for fragment in fragments
            if fragment.name_fragment.lower() in name.lower()
        ]

        if len(matches) > 1:
            raise RuntimeError("Database integrity fault: multiple fragment matches")

        if len(matches) == 1:
            return matches[0]
