"""

"""
from cleo import Command

from starling_server.cli.commands.name.name_add import NameAdd
from starling_server.cli.commands.name.name_init import NameInit
from starling_server.cli.commands.name.name_reset import (
    NameReset,
)


class NameCommand(Command):
    """
    Manage Banks and associated accounts.

    name
    """

    commands = [NameReset(), NameAdd(), NameInit()]

    def handle(self):
        # TODO list names

        if self.option("help"):
            return self.call("help", self._config.name)
