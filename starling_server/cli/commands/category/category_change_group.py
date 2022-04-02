from cleo import Command

from starling_server.main import db
from starling_server.server.mappers.category_mapper import CategoryMapper

category_mapper = CategoryMapper(db=db)


class CategoryChangeGroup(Command):
    """
    Change the group of a category.

    change
        {group : The category group}
        {category : The category name}
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
            f"<info>  Changing category group for`{group_name.capitalize()}:{category_name.capitalize()}`...</info>"
        )

        categories = db.categories_select()

        groups = []
        for c in categories:
            if c.group not in groups:
                groups.append(c.group)

        # get the new group from the user
        valid_response = False
        option = None

        while not valid_response:
            self.line("Please select a group ('q' to quit):")
            for idx, group in enumerate(groups):
                self.line(f"[{idx}] {group.name}")
            option = self.ask("> ")
            if option == "q" or option is None:
                self.line("Exiting")
                return
            if int(option) > len(groups):
                self.line("Invalid option")
                continue
            valid_response = True

        new_group = groups[int(option)]
        new_category = category_mapper.change_category_group(category, new_group)

        self.line(
            f"<info>Changed category group to `{new_category.group.name}:{new_category.name}`</info>"
        )
