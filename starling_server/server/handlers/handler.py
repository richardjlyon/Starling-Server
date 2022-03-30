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
        self.accounts = [
            Account(account_schema)
            for account_schema in database.select_accounts(as_schema=True)
        ]
