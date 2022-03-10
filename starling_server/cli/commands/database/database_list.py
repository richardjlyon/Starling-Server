import asyncio

from cleo import Command

from starling_server.db.edgedb.database import Database


class DatabaseList(Command):
    """
    List the Banks and associated Accounts in the database

    list
         { --d|database=edgedb : Which database }
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        database = self.option("database")
        db = Database(database=database)

        self.line(f"<info>Listing banks from '{database}'</info>")

        accounts = db.get_accounts(as_schema=True)
        for account in accounts:
            self.line(f"<info>- {account.bank_name}: {account.account_name}</info>")
