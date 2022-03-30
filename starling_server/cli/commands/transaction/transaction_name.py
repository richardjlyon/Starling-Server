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
        fragment = self.ask("Display name fragment: ")
        self.dnm.delete(fragment=fragment)
        print(f"Removed {fragment}")

    def insert_name(self) -> None:
        self.line(f"<info>Enter display name information...</info>")
        fragment = self.ask("Display name fragment: ")
        displayname = self.ask("Display name: ")
        self.dnm.upsert(fragment=fragment, displayname=displayname)
        self.line(f"<info>Added {fragment}->{displayname} </info>")

    def show_table(self):
        displaynames = self.dnm.get_all_displaynames()
        if len(displaynames) > 0:
            table = self.table()
            table.set_header_row(["Fragment", "Display name"])
            table.set_rows(
                [
                    [displayname.fragment, displayname.displayname]
                    for displayname in displaynames
                ]
            )
            table.render(self.io)
