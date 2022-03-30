"""
The AccountHandler coordinates fetching account data from the providers and database and returning it to the client.
"""

import asyncio
from typing import List

from starling_server.db.edgedb.database import Database
from starling_server.server.handlers.handler import Handler
from starling_server.server.schemas import AccountSchema


class AccountHandler(Handler):
    """
    A class for fetching account data and returning it to a client.
    """

    def __init__(self, database: Database):
        super().__init__(database=database)

    async def get_accounts(self) -> List[AccountSchema]:
        """Get a list of the accounts stored in the database."""
        return [account.schema for account in self.accounts]

    async def get_account_balances(
        self,
    ):
        """Get a list of current account balances from the providers."""
        return await asyncio.gather(
            *[account.provider.get_account_balance() for account in self.accounts]
        )
