import asyncio

from cleo import Command

from starling_server.main import db


class AccountDelete(Command):
    """
    Delete an account.

    delete
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        self.line("<info>Deleting an account...</info>")

        self.line(
            "<error>WARNING: This destroys information and cannot be undone. Proceed?</error>"
        )
        if not self.confirm("Type 'confirm' to continue", False, "(?i)^(yes)$"):
            self.line("<info>Exit</info>")
            return

        # get the account from the user
        accounts = db.accounts_select()
        valid_response = False
        response = None

        while not valid_response:
            self.line("<info>Enter the account ID ('q' to quit)</info>")
            for idx, account in enumerate(accounts):
                self.line(f"[{idx}] {account.bank_name}: {account.account_name}")

            response = self.ask(
                ">",
            )
            if response == "q":
                self.line("<info>Exit</info>")
                return
            if int(response) <= len(accounts):
                valid_response = True
                break

            self.line("<error>Invalid account</error>")

        # remove it form the database
        account = accounts[int(response)]
        account_uuid = account.uuid
        account_name = f"{account.bank_name}: {account.account_name}"
        db.account_delete(account_uuid)
        self.line(f"<info>Account '{account_name}' deleted</info>")
