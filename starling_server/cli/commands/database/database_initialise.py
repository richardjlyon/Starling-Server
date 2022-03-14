# cli/commands/database/database_initialise.py
#
# Initialise the database.

import asyncio

from cleo import Command

from starling_server.config import tokens_folder
from starling_server.db.edgedb.database import Database
from starling_server.providers.starling.api import API as StarlingAPI
from starling_server.server.route_dispatcher import RouteDispatcher


class DatabaseInitialise(Command):
    """
    Initialise the server from file system tokens

    init
        { --d|database=edgedb : Which database }
        { --w|where : Display the path on your system to the tokens folder }
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):

        if self.option("where"):
            self.line(f"<info>File tokens at `{tokens_folder}'")
            return

        database = self.option("database")
        db = Database(database=database)

        bank_names = [item.stem for item in tokens_folder.iterdir() if item.is_file()]

        if len(bank_names) > 0:
            self.line("<info>Initialising the server</info>")
            self.line(
                f"<info>Found banks {(', ').join(bank_names)} in {tokens_folder}</info>"
            )
        else:
            self.line(f"<error>No bank tokens found in {tokens_folder}</error>")
            self.line(
                "<error>See documentation for how to configure token files</error"
            )

        banks = [StarlingAPI(bank_name=bank_name) for bank_name in bank_names]
        dispatcher = RouteDispatcher(database=db, banks=banks)
        await dispatcher.update_banks_and_accounts()

        accounts = db.get_accounts(as_schema=True)
        for account in accounts:
            self.line(f"<info>- {account.bank_name}: {account.account_name}</info>")
