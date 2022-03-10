# accounts.py
#
# Implement a command for managing banks and accounts.

import asyncio

from cleo import Command


class AccountsCommand(Command):
    """
    Manage banks and accounts

    accounts
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        pass
