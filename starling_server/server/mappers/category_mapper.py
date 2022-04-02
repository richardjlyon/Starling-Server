"""
Categories are mapped to category groups, and to a table of mappings between display names and categories.
This class manages both of those relationships.
"""
from dataclasses import dataclass
from typing import List, Optional

import edgedb

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
        categories = self.db.categories_select()
        categories.sort(key=lambda c: (c.group.name, c.name))
        return categories

    def make_category(self, group_name: str, category_name: str) -> Category:
        """Insert a category in the database."""

        if self._category_exists(group_name, category_name):
            raise ValueError(f"Category `{group_name}:{category_name}` already exists")

        categories = self.db.categories_select()

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
        self.db.category_upsert(category)

        return category

    def delete_category(self, category: Category) -> None:
        """Delete category from the database."""
        try:
            self.db.category_delete(category)
        except DatabaseError as e:
            raise ValueError(f"{e}") from e

    def rename_category(
        self, category: Category, new_group_name: str, new_category_name: str
    ) -> Category:
        """Rename a category in the database."""
        category.group.name = new_group_name.capitalize()
        category.name = new_category_name.capitalize()
        self.db.category_upsert(category)
        return category

    def change_category_group(
        self, category: Category, new_group: CategoryGroup
    ) -> Category:
        """Change the category group of a category."""
        category.group = new_group
        self.db.category_upsert(category)
        return category

    def insert_name_category(self, name_category: NameCategory) -> None:
        """Insert a name-category mapping in the database."""
        self.db.categorymap_upsert(name_category)

    def select_name_categories(self) -> Optional[List[NameCategory]]:
        """Return all categories in the database."""
        results = self.db.categorymap_select_all()
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
        categories = self.db.categories_select()
        if categories:
            for category in categories:
                self.db.category_delete(category)
                self.db.categorygroup_delete(category)

    def _insert_categories(self) -> Optional[List[Category]]:
        category_list = []

        for group_name, categories in cfg.categories.items():
            group = CategoryGroup(name=group_name.capitalize())
            for category_name in categories:
                category = Category(
                    name=category_name.capitalize(),
                    group=group,
                )
                self.db.category_upsert(category)
                category_list.append(category)

        if len(category_list) > 0:
            return category_list
        else:
            return None

    def _find_category_group_from_name(
        self, group_name: str
    ) -> Optional[CategoryGroup]:
        """Find a category group from its name."""
        categories = self.db.categories_select()
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
        categories = self.db.categories_select()
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

    def _category_exists(self, group_name: str, category_name: str) -> bool:
        """Returns true if the category exists."""
        try:
            self.find_category_from_names(group_name, category_name)
            return True
        except ValueError:
            return False

    def _category_for(self, displayname: str) -> Optional[Category]:
        """Matches a category to a displayname and returns it."""

        def to_category(category: edgedb.Set) -> Category:
            return Category(
                uuid=category.uuid,
                name=category.name,
                group=CategoryGroup(
                    uuid=category.category_group.uuid,
                    name=category.category_group.name,
                ),
            )

        entries = self.db.categorymap_select_all()

        if entries is None:
            return None

        # get any specific matches
        for entry in entries:
            if entry.displayname.lower() == displayname.lower():
                return to_category(entry.category)

        # get any generic matches
        for entry in entries:
            if entry.displayname.lower() in displayname.lower():
                return to_category(entry.category)

        return None
