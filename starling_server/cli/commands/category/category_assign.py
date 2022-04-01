from cleo import Command

from starling_server.main import db
from starling_server.server.mappers.category_mapper import CategoryMapper, NameCategory

category_mapper = CategoryMapper(db=db)


class CategoryAssign(Command):
    """
    Assign a category to a counterparty.

    assign
        {counterparty : The displayed name of the counterparty}
    """

    def handle(self) -> None:
        displayname = self.argument("counterparty")

        categories = category_mapper.list_categories()

        # get the category from the user
        valid_response = False
        option = None

        while not valid_response:
            self.line(f"Please select a category for {displayname} ('q' to quit):")
            for idx, c in enumerate(categories):
                self.line(f"[{idx}] {c.group.name}:{c.name}")
            option = self.ask("> ")
            if option == "q" or option is None:
                self.line("Exiting")
                return
            if int(option) > len(categories):
                self.line("Invalid option")
                continue
            valid_response = True

        category = categories[int(option)]
        name_category = NameCategory(displayname, category)
        category_mapper.insert_name_category(name_category)

    def show_table(self):
        name_categories = self.category_map.select_name_categories()
        if name_categories is None:
            return

        table = self.table()
        table.set_header_row(["Name", "Category"])
        table.set_rows(
            [
                [n.displayname, f"{n.category.group.name}:{n.category.name}"]
                for n in name_categories
            ]
        )
        table.render(self.io)
