# config_helper.py
#
# A class to manage server configuration
import importlib

# FIXME populate from ConfigHelper
from starling_server.db.edgedb.database import Database
from starling_server.providers.api_base import BaseAPI

bank_classes = {
    "Starling Personal": "starling",
    "Starling Business": "starling",
    "SpareBanken": "sparebanken",
}


class ConfigHelper:
    """
    A class for managing configuration of the server e.g. add Banks and accounts
    """

    def __init__(self, db: Database):
        self.db = db

    async def initialise_bank(self, bank_name: str, token: str) -> int:
        """
        Initialise a Bank and associated accounts.

        Using an api object initialised with the given bank, retrieves the accounts authorised for the token, and
        inserts the bank and accounts in the database.

        Args:
            bank_name (str): The name of the bank
            token (str): An authorisation token

        Returns:
            The number of accounts added

        """

        # get the accounts
        api_class = get_class_for_bank_name(bank_name)
        api = api_class(bank_name=bank_name, auth_token=token)
        accounts = await api.get_accounts()

        # insert
        for account in accounts:
            self.db.insert_or_update_account(bank_name, account)

        return len(accounts)


def get_class_for_bank_name(bank_name) -> BaseAPI:
    """Returns a class object computed from the bank_name"""
    api_class = bank_classes.get(bank_name)
    module = importlib.import_module(f"starling_server.providers.{api_class}.api_v2")
    class_ = getattr(module, "APIV2")
    return class_
