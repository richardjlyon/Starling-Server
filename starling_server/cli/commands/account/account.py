# commands/database/account.py
#
# Implement comands for managing accounts

from cleo import Command

from starling_server.cli.commands.account.account_add import AccountAdd


class AccountCommand(Command):
    """
    Manage Banks and associated accounts.

    account
    """

    commands = [AccountAdd()]

    def handle(self):
        return self.call("help", self._config.name)
