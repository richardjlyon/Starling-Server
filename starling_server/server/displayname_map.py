from starling_server.db.edgedb.database import Database


class DisplayNameMap:
    """A class for managing entries in the DisplayNameMap table."""

    def __init__(self, db: Database):
        self.db = db

    def upsert(self, fragment: str = None, displayname: str = None) -> None:
        """
        Insert the fragment / display_name pair in NameDisplayname database table.
        Args:
            fragment (str): the name fragment to insert
            display_name (str): the corresponding display_name to insert
        """
        if fragment is None:
            raise ValueError("Fragment cannot be None")
        if displayname is None:
            raise ValueError("Display name cannot be None")

        self.db.display_name_map_upsert(fragment, displayname)

    def delete(self, fragment: str):
        """
        Delete the name / display_name pair from NameDisplayname database table.
        Args:
            fragment (str): the fragment to match
        """
        self.db.display_name_map_delete(fragment)

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
            if entry.fragment.lower() in name.lower():
                return entry.displayname
        return name
