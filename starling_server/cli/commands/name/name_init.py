from cleo import Command

from starling_server.main import db
from starling_server.mappers.name_mapper import NameMapper

name_mapper = NameMapper(db)


class NameInit(Command):
    """
    Initialise names from a config file

    init
    """

    def handle(self) -> None:
        self.line("<info>Initialising names from config</info>")
        self.line(
            "<error>WARNING: This removes current names and cannot be undone. Proceed?</error>"
        )
        if not self.confirm("Type 'yes' to continue", False, "(?i)^(yes)$"):
            self.line("<info>Exit</info>")
            return

        try:
            names = name_mapper.initialise_names()
        except RuntimeError as e:
            self.line(f"<error>ERROR {e}</error>")
            return

        self.line("<info>Added these names from config...</info>")
        self.show_table(names)

    def show_table(self, names):
        table = self.table()
        table.set_header_row(["Name", "Display name"])
        if names:
            table.set_rows([n.name, n.displayname] for n in names)
        table.render(self.io)
