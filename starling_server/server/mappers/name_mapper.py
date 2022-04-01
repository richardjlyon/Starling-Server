"""
To support customising the display name of a counterparty, a table of customisations is stored in the database.
DisplayNameMap is a class for managing its entries.
"""
from dataclasses import dataclass
from typing import List, Optional

from starling_server import cfg
from starling_server.db.edgedb.database import Database


@dataclass
class NameDisplayname:
    name: str
    displayname: str = None


class NameMapper:
    """A class for managing entries in the NameMapper table."""

    def __init__(self, db: Database):
        self.db = db

    def initialise_names(self) -> List[NameDisplayname]:
        """Create a list of names and display names to be used in the database."""

        # load the names from configuration
        try:
            names = [NameDisplayname(**n) for n in cfg.names]
        except AttributeError:
            raise RuntimeError("Unable to load names from config file")

        # remove the old names if there are any
        old_names = self.db.display_name_map_select()
        if old_names:
            for name in old_names:
                self.db.display_name_map_delete(name.name)

        # insert the new ones
        for name in names:
            self.db.display_name_map_upsert(name.name, name.displayname)

        return names

    def insert(self, name: NameDisplayname) -> None:
        """
        Insert the name / displayname pair in NameDisplayname database table.
        """

        self.db.display_name_map_upsert(name.name, name.displayname)

    def delete(self, name: NameDisplayname):
        """
        Delete the name / display_name pair from NameDisplayname database table.
        Args:
            name (str): the fragment to match
        """
        self.db.display_name_map_delete(name.name)

    def change(self, name: NameDisplayname):
        """Change the name"""
        self.db.display_name_map_upsert(name.name, name.displayname)

    def get_all_displaynames(self) -> Optional[List[NameDisplayname]]:
        """
        Returns all the display names in the database.
        """
        entries = self.db.display_name_map_select()
        if entries is None:
            return None

        return [
            NameDisplayname(name=e.name, displayname=e.displayname) for e in entries
        ]

    def displayname_for(self, name: str) -> str:
        """
        Returns the display name for a fragment.
        Args:
            name (str): the name to match
        """
        entries = self.db.display_name_map_select()

        if entries is None:
            return name

        for entry in entries:
            if entry.name.lower() in name.lower():
                return entry.displayname
        return name
