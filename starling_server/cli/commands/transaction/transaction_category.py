import asyncio

from cleo import Command

from starling_server.main import db
from starling_server.server.category_map import CategoryMap


class TransactionCategory(Command):
    """
    Manage transaction categories.

    category
        {--a|add : Add a category}
        {--d|delete : Delete a category}
        {--l|list : List all categories}
    """

    cm = CategoryMap(db)

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):

        if self.option("add"):
            self.add_category()

        if self.option("list"):
            self.show_category_table()

        if self.option("delete"):
            self.delete_category()

        self.show_category_table()

    def add_category(self):
        """Add a category to the database."""
        self.line(f"<info>Adding categories...</info>")

    def list_categories(self):
        """List all categories."""
        categories = self.cm.get_categories()
        if categories is None:
            return

        table = self.table()
        table.set_header_row(["Category Group", "Category"])
        table.set_rows(
            [[category.category_group.name, category.name] for category in categories]
        )

    def delete_category(self):
        """Delete a category from the database."""
        self.line(f"<info>Deleting categories...</info>")

    def show_category_table(self):
        categories = self.cm.get_categories()
        if categories is None:
            return

        table = self.table()
        table.set_header_row(["Category Group", "Category"])
        table.set_rows(
            [[category.category_group.name, category.name] for category in categories]
        )
