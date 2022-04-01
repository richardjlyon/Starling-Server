from cleo import Command

from starling_server.main import db
from starling_server.server.mappers.category_map import CategoryMap

category_mapper = CategoryMap(db=db)


class CategoryRename(Command):
    """
    Rename a category

    rename
        {group : A category group}
        {category : A category name}
    """

    def handle(self) -> None:
        group_name = self.argument("group")
        category_name = self.argument("category")

        try:
            category = category_mapper.find_category_from_names(
                group_name, category_name
            )
        except ValueError as e:
            self.line(f"<error>ERROR: {e}</error>")
            return

        self.line(
            f"<info>  Renaming category `{group_name.capitalize()}:{category_name.capitalize()}`...</info>"
        )

        new_group_name = self.ask(
            f"New category group ({group_name.capitalize()}): ", group_name.capitalize()
        )
        new_category_name = self.ask(
            f"New category name ({category_name.capitalize()}): ",
            category_name.capitalize(),
        )

        renamed_category = category_mapper.rename_category(
            category, new_group_name, new_category_name
        )

        self.line(
            f"<info>Renamed category to `{renamed_category.group.name}:{renamed_category.name}`</info>"
        )
