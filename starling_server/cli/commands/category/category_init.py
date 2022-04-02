from typing import List

from cleo import Command

from starling_server.main import db
from starling_server.mappers.category_mapper import CategoryMapper
from starling_server.schemas.transaction import Category

category_mapper = CategoryMapper(db=db)


class CategoryInit(Command):
    """
    Initialise categories from a config file.

    init
    """

    def handle(self) -> None:

        self.line("<info>Initialising categories from config</info>")
        self.line(
            "<error>WARNING: This removes current categories and cannot be undone. Proceed?</error>"
        )
        if not self.confirm("Type 'yes' to continue", False, "(?i)^(yes)$"):
            self.line("<info>Exit</info>")
            return

        categories = category_mapper.initialise_categories()

        self.line("<info>Added these categories from config...</info>")
        self.show_table(categories)

    def show_table(self, categories: List[Category]):
        table = self.table()
        table.set_header_row(["Group", "Category"])
        if categories:
            table.set_rows([c.group.name, c.name] for c in categories)
        table.render(self.io)
