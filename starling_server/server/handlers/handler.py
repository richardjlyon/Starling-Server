import sys
from typing import List

from starling_server.db.edgedb.database import Database
from starling_server.server.account import Account


class Handler:
    """
    A base class for all handlers.
    """

    db: Database
    accounts: List[Account]

    def __init__(self, database: Database):
        self.db = database
        account_schemas = database.select_accounts()
        if account_schemas:
            self.accounts = [
                Account(account_schema) for account_schema in account_schemas
            ]
        else:
            print("No accounts found in database. Please run `bank_server account add`")
            sys.exit()
