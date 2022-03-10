# cli.py - Command Line Interface
# Richard Lyon, 20 Feb 2022

from cleo import Application as BaseApplication

from starling_server import __version__
from starling_server.cli.commands import (
    ServerCommand,
    AccountsCommand,
    DatabaseCommand,
)


class Application(BaseApplication):
    """A comment"""

    def __init__(self):
        super(Application, self).__init__("bank_server", __version__)
        commands = [
            ServerCommand(),
            AccountsCommand(),
            DatabaseCommand(),
        ]
        for command in commands:
            self.add(command)


cli_app = Application()


def cli():
    cli_app.run()


if __name__ == "__main__":
    cli()
