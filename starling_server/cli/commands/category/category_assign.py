import asyncio

from cleo import Command

from starling_server.main import db
from starling_server.server.mappers.category_mapper import CategoryMapper


class CategoryAssign(Command):
    """
    Assign a category to a counterparty.

    assign
    """

    category_map = CategoryMapper(db)

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        self.show_table()

    def show_table(self):
        name_categories = self.category_map.select_name_categories()
        if name_categories is None:
            return

        table = self.table()
        table.set_header_row(["Name", "Category"])
        table.set_rows(
            [
                [n.displayname, f"{n.category.group.name}:{n.category.name}"]
                for n in name_categories
            ]
        )
        table.render(self.io)
