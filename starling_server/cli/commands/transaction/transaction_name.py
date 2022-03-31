import asyncio

from cleo import Command

from starling_server.main import db
from starling_server.server.displayname_map import DisplayNameMap


class TransactionName(Command):
    """
    Manage display name modifiers

    names
        {--d|delete : Delete a display name modifier}
        {--a|add : Add a display name modifier}
    """

    dnm = DisplayNameMap(db)

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):

        self.show_table()

        if self.option("delete"):
            self.delete_name()

        elif self.option("add"):
            self.insert_name()

        self.show_table()

    def delete_name(self) -> None:
        self.line(f"<info>Delete name...</info>")
        name = self.ask("Counterparty name: ")
        self.dnm.delete(name=name)
        print(f"Removed {name}")

    def insert_name(self) -> None:
        self.line(f"<info>Enter display name information...</info>")
        name = self.ask("Counterparty name: ")
        displayname = self.ask("Display name: ")
        self.dnm.upsert(name=name, displayname=displayname)
        self.line(f"<info>Added {name}->{displayname} </info>")

    def show_table(self):
        displaynames = self.dnm.get_all_displaynames()
        if len(displaynames) == 0:
            return

        table = self.table()
        table.set_header_row(["Fragment", "Display name"])
        table.set_rows(
            [
                [displayname.name, displayname.displayname]
                for displayname in displaynames
            ]
        )
        table.render(self.io)
