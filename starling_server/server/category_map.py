"""
Categories are mapped to category groups, and to a table of mappings between display names and categories.
This class manages both of those relationships.
"""
import uuid
from typing import List

from starling_server.db.edgedb.database import Database
from starling_server.server.schemas.transaction import Category


class CategoryMap:
    """A class to manage the mapping between categories and category groups, and display names."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def upsert_category(self, category: Category) -> None:
        """Insert or update category in the database."""
        pass

    def delete_category(self, category_uuid: uuid.UUID) -> None:
        """Delete category from the database."""
        pass

    def upsert_categorymap(self, displayname: str, category: Category) -> None:
        """Insert or update a displayname to category mapping in the database."""
        pass

    def delete_categorymap(self, displayname: str) -> None:
        """Delete a displayname to category mapping from the database."""

    def select_categories(self) -> List[Category]:
        """Return all categories in the database."""
        pass
