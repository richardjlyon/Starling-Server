import asyncio

from cleo import Command

from starling_server.db.edgedb.database import Database


class DatabaseReset(Command):
    """
    Delete Banks and Accounts from the database and repopulate

    reset
         { --d|database=edgedb : Which database }
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        database = self.option("database")
        db = Database(database=database)

        self.line(f"<info>Resetting '{database}'</info>")
        if not self.confirm(
            "<error>WARNING: This will destroy all data and cannot be undone: continue?</error>",
            False,
        ):
            self.line("<info>Abandoned</info>")
