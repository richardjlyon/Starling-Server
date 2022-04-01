from cleo import Command

from starling_server.main import db
from starling_server.server.mappers.name_mapper import NameMapper, NameDisplayname

name_mapper = NameMapper(db)


class NameAdd(Command):
    """
    Add a name

    add
        {name : Counterparty name}
        {displayname : Displayname}
    """

    def handle(self) -> None:
        name = self.argument("name")
        displayname = self.argument("displayname")
        name = NameDisplayname(name, displayname)

        self.line(
            f"<info>  Adding display name '{name.name}'-> '{name.displayname}'...</info>"
        )

        name_mapper.insert(name)
        names = name_mapper.get_all_displaynames()
        self.show_table(names)

    def show_table(self, names):
        table = self.table()
        table.set_header_row(["Name", "Display name"])
        if names:
            table.set_rows([n.name, n.displayname] for n in names)
        table.render(self.io)
