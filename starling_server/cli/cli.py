# cli.py - Command Line Interface
# Richard Lyon, 20 Feb 2022
import asyncio
import os

from cleo import Command, Application

from starling_server.config.Config import CONFIG, TOKENS_FOLDER


class InitCommand(Command):
    """
    Initialise Starling Server configuration file from access tokens

    init
    """

    def handle(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        if not self.confirm(
            "WARNING: This will reset configuration data. Continue?", False
        ):
            return

        os.makedirs(CONFIG.saveFolderPath(), exist_ok=True)

        # get tokens from files
        if not TOKENS_FOLDER.is_dir():
            os.mkdir(TOKENS_FOLDER)
            self.line(f"<error>no tokens folder</error>")
            self.line(f"<error>created tokens folder at {TOKENS_FOLDER}</error>")
            self.line(
                "<error>create a file for each token in tokens folder and rerun 'init'</error>"
            )
            self.line("Done")
            return

        print(TOKENS_FOLDER)


class ServerCommand(Command):
    """
    Start the Starling Server

    go
    """

    def handle(self):
        import uvicorn

        uvicorn.run("starling_server.app:app", host="0.0.0.0", port=8080, reload=True)


cli_app = Application()
cli_app.add(InitCommand())
cli_app.add(ServerCommand())


def cli():
    cli_app.run()


if __name__ == "__main__":
    cli()
