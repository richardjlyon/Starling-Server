import asyncio

from cleo import Command


class AccountDelete(Command):
    """
    Delete an account.

    delete
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        self.line("<info>Deleting an account</info>")

        # get the account from the user
        self.line(
            "<error>WARNING: This destroys information and cannot be undone</error>"
        )
        if not self.confirm("Type 'confirm' to continue", False, "(?i)^(confirm)$"):
            self.line("<info>Exit</info>")
            return

        self.line("deleting")

        # remove it from the database

        # if it's the last account, remove the bank from the database

        # perform api specific actions

        # inform

        pass
