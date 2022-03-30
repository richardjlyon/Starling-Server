"""

"""
from cleo import Command

from starling_server.cli.commands.transaction.transaction_delete import (
    TransactionDelete,
)
from starling_server.cli.commands.transaction.transaction_name import TransactionName
from starling_server.cli.commands.transaction.transaction_update import (
    TransactionUpdate,
)


class TransactionCommand(Command):
    """
    Manage Banks and associated accounts.

    transactions
    """

    commands = [TransactionUpdate(), TransactionDelete(), TransactionName()]

    def handle(self):
        if self.option("help"):
            return self.call("help", self._config.name)
