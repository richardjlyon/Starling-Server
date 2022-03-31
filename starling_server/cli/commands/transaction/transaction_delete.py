import asyncio

from cleo import Command

from starling_server.main import db


class TransactionDelete(Command):
    """
    Delete transactions from the specified account

    delete
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        self.line("<info>Deleting transactions...</info>")

        # warn before deleting
        self.line(
            "<error>WARNING: This destroys information and cannot be undone. Proceed?</error>"
        )
        if not self.confirm("Type 'yes' to continue", False, "(?i)^(yes)$"):
            self.line("<info>Exit</info>")
            return

        # get the account from the user
        accounts = db.select_accounts()
        for account in accounts:
            db.delete_transactions_for_account_id(account.uuid)

        self.line("<info>Done</info>")
