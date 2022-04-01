from cleo import Command

from starling_server.db.edgedb.database import DatabaseError
from starling_server.main import db
from starling_server.server.mappers.category_map import CategoryMap

category_mapper = CategoryMap(db=db)


class CategoryDelete(Command):
    """
    Delete a category.

    delete
        {group : The category group}
        {category : The category name}
    """

    def handle(self) -> None:
        group_name = self.argument("group")
        category_name = self.argument("category")

        if not self.confirm(
            f"<info>Deleting category `{group_name.capitalize()}:{category_name.capitalize()}`. Type 'yes' to continue</info>",
            False,
            "(?i)^(yes)$",
        ):
            self.line("<info>Exit</info>")
            return

        try:
            category_mapper.delete_category(group_name, category_name)
        except ValueError as e:
            self.line(f"<error>ERROR: {e}</error>")
        except DatabaseError as e:
            self.line(f"<error>ERROR: {e}</error>")
            return

        self.line(
            f"<info>Category `{group_name.capitalize()}:{category_name.capitalize()}` deleted</info>"
        )
