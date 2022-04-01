import asyncio
from typing import List

from cleo import Command

from starling_server import cfg
from starling_server.main import db
from starling_server.server.schemas.transaction import Category, CategoryGroup


class CategoryInit(Command):
    """
    Initialise categories from a config file.

    init
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        self.line("<info>Initialising categories from config</info>")
        self.line(
            "<error>WARNING: This removes current categories and cannot be undone. Proceed?</error>"
        )
        if not self.confirm("Type 'yes' to continue", False, "(?i)^(yes)$"):
            self.line("<info>Exit</info>")
            return

        delete_all_categories()
        categories = insert_categories()
        # TODO delete CategoryMap table

        self.line("<info>Added these categories from config...</info>")
        self.show_table(categories)

    def show_table(self, categories: List[Category]):
        table = self.table()
        table.set_header_row(["Group", "Category"])
        if categories:
            table.set_rows([c.group.name, c.name] for c in categories)
        table.render(self.io)


def delete_all_categories():
    categories = db.select_categories()
    if categories:
        for category in categories:
            db.delete_category(category)
            db.delete_category_group(category)


def insert_categories() -> List[Category]:
    category_list = []
    for group_name, categories in cfg.categories.items():
        group = CategoryGroup(name=group_name.capitalize())
        for category_name in categories:
            category = Category(
                name=category_name.capitalize(),
                group=group,
            )
            db.upsert_category(category)
            category_list.append(category)

    return category_list
