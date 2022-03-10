# cli.py - Command Line Interface
# Richard Lyon, 20 Feb 2022

from cleo import Application

from starling_server.cli.commands import AccountsCommand, ServerCommand

cli_app = Application()
cli_app.add(ServerCommand())
cli_app.add(AccountsCommand())


def cli():
    cli_app.run()


if __name__ == "__main__":
    cli()

# class InitCommand(Command):
#     """
#     Initialise Starling Server configuration file from access tokens
#
#     init
#     """
#
#     def handle(self):
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(self.handle_async())
#
#     async def handle_async(self):
#         if not self.confirm(
#             "WARNING: This will reset configuration data. Continue?", False
#         ):
#             return
#
#         os.makedirs(CONFIG.saveFolderPath(), exist_ok=True)
#
#         # get tokens from files
#         if not TOKENS_FOLDER.is_dir():
#             os.mkdir(TOKENS_FOLDER)
#             self.line(f"<error>no tokens folder</error>")
#             self.line(f"<error>created tokens folder at {TOKENS_FOLDER}</error>")
#             self.line(
#                 "<error>create a file for each token in tokens folder and rerun 'init'</error>"
#             )
#             self.line("Done")
#             return
#
#         print(TOKENS_FOLDER)
