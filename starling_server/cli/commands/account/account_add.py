import asyncio
from dataclasses import dataclass
from typing import Type, Optional

from cleo import Command

from starling_server import cfg
from starling_server.main import db
from starling_server.providers.provider import Provider
from starling_server.server.account import get_provider_class, get_auth_token


@dataclass
class BankInfo:
    bank_name: str
    provider: Type[Provider]
    auth_token: str


class AccountAdd(Command):
    """
    Add the accounts associated with a bank.

    add
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        self.line("Adding account")

        # get the bank name and authentication token
        provider = self.get_bank_provider()
        if provider is None:
            return

        # get the accounts associated with the bank
        accounts = await provider.get_accounts()

        # insert the accounts into the database
        if len(accounts) > 0:
            # upsert the bank in the database
            db.bank_upsert(provider.bank_name)

        for account in accounts:
            self.line(f"Adding account {account.account_name}")
            db.account_upsert(provider.auth_token, account)

    def get_bank_provider(self) -> Optional[Provider]:
        """Get the bank provider class and authentication token."""
        bank_names = [bank["bank_name"] for bank in cfg.banks]
        valid_response = False
        bank_name = None
        option = None

        # get the bank name from user
        while not valid_response:
            self.line("Please select a bank ('q' to quit):")
            for idx, bank_name in enumerate(bank_names):
                self.line(f"[{idx}] {bank_name}")
            option = self.ask("> ")
            if option == "q" or option is None:
                self.line("Exiting")
                return
            if int(option) > len(bank_names):
                self.line("Invalid option")
                continue
            valid_response = True

        # construct the provider object
        provider = get_provider_class(bank_name)
        bank_name = bank_names[int(option)]
        auth_token = get_auth_token(bank_name)

        return provider(
            auth_token=auth_token,
            bank_name=bank_name,
            category_check=False,
        )
