from cleo import Command

from starling_server.main import db
from starling_server.mappers.name_mapper import NameDisplayname, NameMapper

name_mapper = NameMapper(db)


class NameDelete(Command):
    """
    Delete a name

    delete
        {name : Counterparty name}
    """

    def handle(self) -> None:
        name = self.argument("name")

        self.line(f"<info>  Delete display name for '{name}'...</info>")
        name_mapper.delete(NameDisplayname(name=name))
        names = name_mapper.get_all_displaynames()
        self.show_table(names)

    def show_table(self, names):
        table = self.table()
        table.set_header_row(["Name", "Display name"])
        if names:
            table.set_rows([n.name, n.displayname] for n in names)
        table.render(self.io)
