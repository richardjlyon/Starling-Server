import asyncio

from cleo import Command

from starling_server.main import db
from starling_server.server.displayname_map import DisplayNameMap


class TransactionName(Command):
    """
    Manage display name modifiers

    name
        {--d|delete : Delete a display name modifier}
    """

    dnm = DisplayNameMap(db)

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        if self.option("delete"):
            self.delete_name()
        else:
            self.insert_name()

    def delete_name(self) -> None:
        fragment = self.ask("Display name fragment: ")
        self.dnm.delete(fragment=fragment)
        print(f"Removed {fragment}")

    def insert_name(self) -> None:
        self.line(f"<info>Enter display name information...</info>")
        fragment = self.ask("Display name fragment: ")
        displayname = self.ask("Display name: ")
        self.dnm.upsert(fragment=fragment, displayname=displayname)
        self.line(f"<info>Added {fragment}->{displayname} </info>")
