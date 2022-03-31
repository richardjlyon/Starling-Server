# commands/database/account.py
#
# Implement comands for managing accounts

from cleo import Command

from starling_server.cli.commands.account.account_add import AccountAdd
from starling_server.cli.commands.account.account_delete import AccountDelete
from starling_server.main import db


class AccountCommand(Command):
    """
    Manage Banks and associated accounts.

    account
    """

    commands = [AccountAdd(), AccountDelete()]

    def handle(self):

        accounts = db.select_accounts()

        if accounts is None:
            return

        for idx, account in enumerate(accounts):
            # TODO add account balances
            self.line(
                f"<info>[{idx}] {account.bank_name}: {account.account_name}</info>"
            )

        if self.option("help"):
            return self.call("help", self._config.name)
