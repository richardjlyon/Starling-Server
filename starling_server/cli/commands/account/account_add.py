import asyncio
from pathlib import Path
from typing import Optional

from cleo import Command

from starling_server.main import db
from starling_server.providers.starling.api_v2 import CategoryHelper
from starling_server.server.config_helper import ConfigHelper
from starling_server.server.config_helper import bank_classes

config = ConfigHelper(db)


class AccountAdd(Command):
    """
    Add a Bank and associated accounts to the database.

    add
    """

    # FIXME This is broken until adapted to use Starling APIV2.

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
        accounts = await config.initialise_bank(bank_name=bank_name, token=token)

        # If it's a Starling bank, add the account's default category to the config file
        if bank_classes.get(bank_name) == "starling":
            category_helper = CategoryHelper()
            for account in accounts:
                await category_helper.insert(
                    token=token, account_uuid=account.uuid, bank_name=bank_name
                )

        # self.line(f"<info>Added {accounts_added} account(s)</info>")
        self.line("<info>Added account</info>")
        for account in accounts:
            self.line(f"<info> - {account.bank_name}: {account.account_name}</info>")
        self.line("<info>Done</info>")

    def get_bank_name(self) -> str:
        bank_names = list(bank_classes.keys())
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

    # def get_accounts_for_bank_name(self, bank_name: str, auth_token: str):
    #     """Get the accounts associated with the auth_token from the bank"""
    #     api_class = get_class_for_bank_name(bank_name)
    #
    #     api = api_class()


def get_token_from_file(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read().strip()
