"""

"""
from cleo import Command

from starling_server.cli.commands.name.name_add import NameAdd
from starling_server.cli.commands.name.name_change import NameChange
from starling_server.cli.commands.name.name_delete import NameDelete
from starling_server.cli.commands.name.name_init import NameInit


class NameCommand(Command):
    """
    Manage Banks and associated accounts.

    name
    """

    commands = [NameAdd(), NameInit(), NameDelete(), NameChange()]

    def handle(self):
        # TODO list names

        if self.option("help"):
            return self.call("help", self._config.name)
