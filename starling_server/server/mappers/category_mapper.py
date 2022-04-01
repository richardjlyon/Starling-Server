"""
Categories are mapped to category groups, and to a table of mappings between display names and categories.
This class manages both of those relationships.
"""
from dataclasses import dataclass
from typing import List, Optional

from starling_server import cfg
from starling_server.db.edgedb.database import Database, DatabaseError
from starling_server.server.schemas.transaction import Category, CategoryGroup


@dataclass
class NameCategory:
    displayname: str
    category: Category


class CategoryMapper:
    """A class to manage the mapping between categories and category groups, and display names."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def initialise_categories(self) -> Optional[List[Category]]:
        """Create the initial set of categories in the database from config data."""
        self._delete_all_categories()
        categories = self._insert_categories()
        # TODO delete CategoryMap table
        return categories

    def list_categories(self) -> List[Category]:
        """Return a list of all categories in the database."""
        categories = self.db.select_categories()
        categories.sort(key=lambda c: (c.group.name, c.name))
        return categories

    def make_category(self, group_name: str, category_name: str) -> Category:
        """Insert a category in the database."""

        if self.find_category_from_names(group_name, category_name):
            raise ValueError(f"Category `{group_name}:{category_name}` already exists")

        categories = self.db.select_categories()

        # find or create the group
        group = self._find_category_group_from_name(group_name)
        if group is None:
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

    def delete_category(self, category: Category) -> None:
        """Delete category from the database."""
        try:
            self.db.delete_category(category)
        except DatabaseError as e:
            raise ValueError(f"{e}") from e

    def rename_category(
        self, category: Category, new_group_name: str, new_category_name: str
    ) -> Category:
        """Rename a category in the database."""
        category.group.name = new_group_name.capitalize()
        category.name = new_category_name.capitalize()
        self.db.upsert_category(category)
        return category

    def change_category_group(
        self, category: Category, new_group: CategoryGroup
    ) -> Category:
        """Change the category group of a category."""
        category.group = new_group
        self.db.upsert_category(category)
        return category

    def insert_name_category(self, name_category: NameCategory) -> None:
        """Insert a name-category mapping in the database."""
        self.db.upsert_name_category(name_category)

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

    def _find_category_group_from_name(
        self, group_name: str
    ) -> Optional[CategoryGroup]:
        """Find a category group from its name."""
        categories = self.db.select_categories()
        try:
            result = next(
                c.group
                for c in categories
                if c.group.name.lower() == group_name.lower()
            )
        except StopIteration:
            result = None

        return result

    def find_category_from_names(self, group_name: str, category_name: str) -> Category:
        """Returns a category identified by its group and category name."""

        # find the group
        group = self._find_category_group_from_name(group_name)
        if group is None:
            raise ValueError(
                f"Category group `{group_name.capitalize()}` does not exist"
            )

        # find the category
        categories = self.db.select_categories()
        try:
            category = next(
                c
                for c in categories
                if c.name.lower() == category_name.lower() and c.group == group
            )
        except StopIteration:
            raise ValueError(
                f"Category name `{category_name.capitalize()}` does not exist"
            )

        return category

    def category_for(self, display_name: str) -> Category:
        """Returns a category identified by its display name."""
