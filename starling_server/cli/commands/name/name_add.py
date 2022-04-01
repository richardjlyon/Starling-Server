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

        name_mapper.add(name)

    #     self.show_table()
    #
    #     if self.option("delete"):
    #         self.delete_name()
    #
    #     elif self.option("add"):
    #         self.insert_name()
    #
    #     self.show_table()
    #
    # def delete_name(self) -> None:
    #     self.line(f"<info>Delete name...</info>")
    #     name = self.ask("Counterparty name: ")
    #     self.dnm.delete(name=name)
    #     print(f"Removed {name}")
    #
    # def insert_name(self) -> None:
    #     self.line(f"<info>Enter display name information...</info>")
    #     name = self.ask("Counterparty name: ")
    #     displayname = self.ask("Display name: ")
    #     self.dnm.upsert(name=name, displayname=displayname)
    #     self.line(f"<info>Added {name}->{displayname} </info>")
