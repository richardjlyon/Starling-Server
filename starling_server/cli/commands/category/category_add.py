import asyncio
from typing import List

from cleo import Command

from starling_server.main import db
from starling_server.server.schemas.transaction import Category


class CategoryAdd(Command):
    """
    Add a new category to the database.

    add
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        self.line("<info>Adding category</info>")
        categories = db.select_categories()
        self.show_table(categories)

    def show_table(self, categories: List[Category]):
        table = self.table()
        table.set_header_row(["Group", "Category"])
        if categories:
            table.set_rows([[c.group.name, c.name]] for c in categories)
        table.render(self.io)
