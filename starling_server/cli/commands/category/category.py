from typing import List

from cleo import Command

from starling_server.cli.commands.category.category_add import CategoryAdd
from starling_server.cli.commands.category.category_init import CategoryInit
from starling_server.main import db
from starling_server.server.schemas.transaction import Category


class CategoryCommand(Command):
    """
    Manage adding, assigning, modifying, and removing categories.

    category
    """

    commands = [CategoryAdd(), CategoryInit()]

    def handle(self):

        categories = db.select_categories()
        self.show_table(categories)

        if categories is None:
            return

        for category in categories:
            self.line(f"<info>{category.name}</info>")

        if self.option("help"):
            return self.call("help", self._config.name)

    def show_table(self, categories: List[Category]):
        table = self.table()
        table.set_header_row(["Group", "Category"])
        if categories:
            table.set_rows([[c.group.name, c.name]] for c in categories)
        table.render(self.io)
