from typing import List

from cleo import Command

from starling_server.main import db
from starling_server.server.mappers.category_mapper import CategoryMapper
from starling_server.server.schemas.transaction import Category

category_mapper = CategoryMapper(db=db)


class CategoryAdd(Command):
    """
    Add a new category to the database.

    add
        {group : A category group}
        {category : A category name}
    """

    def handle(self) -> None:

        group_name = self.argument("group")
        category_name = self.argument("category")

        self.line(
            f"<info>  Adding category `{group_name.capitalize()}:{category_name.capitalize()}`...</info>"
        )

        try:
            category = category_mapper.make_category(
                group_name=group_name, category_name=category_name
            )
        except ValueError as e:
            self.line(f"<error>ERROR: {e}</error>")
            return

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
