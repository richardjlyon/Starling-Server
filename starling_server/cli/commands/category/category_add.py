from typing import List

from cleo import Command

from starling_server.main import db
from starling_server.server.schemas.transaction import Category, CategoryGroup


class CategoryAdd(Command):
    """
    Add a new category to the database.

    add
        {group : A category group}
        {category : A category name}
    """

    def handle(self) -> None:

        self.line("<info>Add a category...</info>")
        categories = db.select_categories()

        group = self.argument("group")
        category = self.argument("category")

        # find or create the group
        try:
            group = next(
                c.group for c in categories if c.group.name.lower() == group.lower()
            )
        except StopIteration:
            group = CategoryGroup(name=group)

        # if `category` name already exists in group, fail
        category_names = [c.name.lower() for c in categories if c.group == group]
        if category.lower() in category_names:
            self.line(
                f"<error>Category `{category.capitalize()}` already exists in group `{group.name}`</error>"
            )
            return  # exit

        # insert the new category
        category = Category(name=category, group=group)
        db.upsert_category(category)

        categories = db.select_categories()
        categories.sort(key=lambda c: (c.group.name, c.name))
        for c in categories:
            if c.name == category.name:
                marker = "*"
            else:
                marker = " "
            self.line(f"{marker} {c.group.name}:{c.name}")

    def show_category_table(self, categories: List[Category], sort: bool = True):
        if sort:
            categories.sort(key=lambda c: (c.group.name, c.name))
        table = self.table()
        table.set_header_row(["", "Category"])
        if categories:
            for idx, category in enumerate(categories):
                table.add_row([str(idx), f"{category.group.name}:{category.name}"])
            table.render(self.io)
