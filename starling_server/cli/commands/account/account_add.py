import asyncio
from pathlib import Path
from typing import Optional, List

from cleo import Command

from starling_server import cfg
from starling_server.db.edgedb.database import Database
from starling_server.main import db
from starling_server.providers.starling.api import CategoryHelper
from starling_server.server.route_dispatcher import get_provider_for_bank_name
from starling_server.server.schemas.account import AccountSchema


class AccountAdd(Command):
    """
    Add an account.

    add
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        self.line("Adding account")

        # get the bank name and authentication token
        bank_name = self.get_bank_name()
        try:
            token = self.get_token()
        except RuntimeError as e:
            self.line(f"<error>{e}.</error>")
            return

        # add them to the database
        accounts = await initialise_bank(database=db, bank_name=bank_name, token=token)

        # If it's a Starling bank, add the account's default category to the config file
        if cfg.bank_classes.get(bank_name) == "starling":
            category_helper = CategoryHelper()
            for account in accounts:
                await category_helper.insert(
                    token=token, account_uuid=account.uuid, bank_name=bank_name
                )

        self.line("<info>Added account</info>")
        for account in accounts:
            self.line(f"<info> - {account.bank_name}: {account.account_name}</info>")
        self.line("<info>Done</info>")

    def get_bank_name(self) -> str:
        bank_names = list(cfg.bank_classes.keys())
        bank_name = self.choice("Enter the name of the bank", bank_names)
        return bank_name

    def get_token(self) -> Optional[str]:
        filepath = None
        token = None
        while not self.is_valid_token_file(filepath):
            filepath = self.ask(
                "Authorisation token filepath ('return' to quit)",
                "/Users/richardlyon/Library/Preferences/com.rjlyon.starling_server/tokens/Starling Business",
            )
            if filepath is None:
                raise RuntimeError("Quit")

        return get_token_from_file(filepath)

    def is_valid_token_file(self, filepath: str) -> bool:
        """Return true if filepath is a valid token file. Valid means it exists and contains text."""
        if filepath is None:
            return False

        p = Path(filepath)
        if not p.is_file():
            self.line(f"<error>No token found for file '{str(filepath)}'")
            return False

        token = get_token_from_file(p)
        if len(token) == 0:
            self.line(f"<error>Invalid token for file</error>")
            return False

        return True


def get_token_from_file(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read().strip()


async def initialise_bank(
    database: Database, bank_name: str, token: str
) -> List[AccountSchema]:
    """
    Initialise a Bank and associated accounts.

    Using an api object initialised with the given bank, retrieves the accounts authorised for the token, and
    inserts the bank and accounts in the database.

    Args:
        database: The database to insert the bank and accounts into.
        bank_name (str): The name of the bank
        token (str): An authorisation token

    Returns:
        The number of accounts added

    """

    # get the accounts
    provider_class = get_provider_for_bank_name(bank_name)
    provider = provider_class(bank_name=bank_name, auth_token=token)
    accounts = await provider.get_accounts()

    # insert into the database
    for account in accounts:
        database.upsert_account(token=token, account=account)

    return accounts
