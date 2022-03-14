# commands/database/database.py
#
# Implement commands for managing the EdgeDB database.

from cleo import Command

from .database_initialise import DatabaseInitialise
from .database_list import DatabaseList
from .database_reset import DatabaseReset


class DatabaseCommand(Command):
    """
    Manage the EdgeDB database instance.

    db
    """

    commands = [DatabaseReset(), DatabaseList(), DatabaseInitialise()]

    def handle(self):
        return self.call("help", self._config.name)
