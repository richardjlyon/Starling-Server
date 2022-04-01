"""
Categories are mapped to category groups, and to a table of mappings between display names and categories.
This class manages both of those relationships.
"""
import uuid
from dataclasses import dataclass
from typing import List, Optional

from starling_server import cfg
from starling_server.db.edgedb.database import Database
from starling_server.server.schemas.transaction import Category, CategoryGroup


@dataclass
class NameCategory:
    displayname: str
    category: Category


class CategoryMap:
    """A class to manage the mapping between categories and category groups, and display names."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def initialise_categories(self) -> Optional[List[Category]]:
        """Create the initial set of categories in the database from config data."""
        self._delete_all_categories()
        categories = self._insert_categories()
        # TODO delete CategoryMap table
        return categories

    def upsert_category(
        self, group_name: str, category_name: str
    ) -> Optional[Category]:
        """Insert or update category in the database."""

        categories = self.db.select_categories()

        # find or create the group
        try:
            group = next(
                c.group
                for c in categories
                if c.group.name.lower() == group_name.lower()
            )
        except StopIteration:
            group = CategoryGroup(name=group_name)

        # if `category` name already exists in group, fail
        category_names = [c.name.lower() for c in categories if c.group == group]
        if category_name.lower() in category_names:
            raise ValueError(
                f"Category {category_name} already exists in group {group_name}"
            )

        # insert the new category
        category = Category(name=category_name, group=group)
        self.db.upsert_category(category)

        return category

    def delete_category(self, category_uuid: uuid.UUID) -> None:
        """Delete category from the database."""
        pass

    def upsert_categorymap(self, displayname: str, category: Category) -> None:
        """Insert or update a displayname to category mapping in the database."""
        pass

    def delete_categorymap(self, displayname: str) -> None:
        """Delete a displayname to category mapping from the database."""

    def select_name_categories(self) -> Optional[List[NameCategory]]:
        """Return all categories in the database."""
        results = self.db.get_all_name_categories()
        if results is None:
            return None

        return [
            NameCategory(
                displayname=r.displayname,
                category=Category(
                    uuid=r.category.uuid,
                    name=r.category.name,
                    group=CategoryGroup(
                        uuid=r.category.category_group.uuid,
                        name=r.category.category_group.name,
                    ),
                ),
            )
            for r in results
        ]

    def _delete_all_categories(self):
        categories = self.db.select_categories()
        if categories:
            for category in categories:
                self.db.delete_category(category)
                self.db.delete_category_group(category)

    def _insert_categories(self) -> Optional[List[Category]]:
        category_list = []

        for group_name, categories in cfg.categories.items():
            group = CategoryGroup(name=group_name.capitalize())
            for category_name in categories:
                category = Category(
                    name=category_name.capitalize(),
                    group=group,
                )
                self.db.upsert_category(category)
                category_list.append(category)

        if len(category_list) > 0:
            return category_list
        else:
            return None
