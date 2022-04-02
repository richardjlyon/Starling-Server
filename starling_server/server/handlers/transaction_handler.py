"""
The TransactionHandler coordinates fetching new transactions from the provider, setting display name and category
information, archiving to the database, and returning to the client.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from starling_server import cfg
from starling_server.db.edgedb.database import Database
from starling_server.server.handlers.account import Account
from starling_server.server.handlers.handler import Handler
from starling_server.server.mappers.category_mapper import CategoryMapper
from starling_server.server.mappers.name_mapper import NameMapper
from starling_server.server.schemas import TransactionSchema


class TransactionHandler(Handler):
    """
    A class for fetching data, archiving it, and returning it to the client.
    """

    def __init__(self, database: Database):
        super().__init__(database=database)

    async def get_transactions_between(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[List[TransactionSchema]]:
        """Get a list of transactions between the given dates.

        This method retrieves new transactions from the providers, stores them in the database, sets each new
        transaction's counter party and category, then returns a list of transactions for the specified interval.
        """

        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=cfg.default_interval_days)

        # Fetch new transactions from the providers and insert them into the database
        new_transactions = await self.get_new_transactions()
        self.insert_transactions(new_transactions)
        transactions = self.db.transactions_select_between(start_date, end_date)
        transactions = self.apply_displayname_and_category(transactions)

        return transactions

    async def get_new_transactions(self) -> Optional[List[TransactionSchema]]:
        """Get all transactions for each account since the last recorded transaction date and insert in the database."""
        transactions = []

        for account in self.accounts:
            latest_transaction_time = self.get_latest_transaction_time(account)
            new_transactions = await account.provider.get_transactions_between(
                start_date=latest_transaction_time, end_date=datetime.now()
            )
            if len(new_transactions) > 0:
                transactions.extend(new_transactions)

        return transactions

    def insert_transactions(self, transactions: List[TransactionSchema]) -> None:
        """Insert transactions into the database."""
        for transaction in transactions:
            self.db.transaction_upsert(transaction)

    def get_latest_transaction_time(self, account: Account) -> Optional[datetime]:
        """Returns the time of the latest transaction for the specified account."""

        transactions = self.db.transactions_select_for_account_uuid(account.schema.uuid)

        if transactions is None:
            # no transactions: compute from the default interval
            transaction_time = datetime.now() - timedelta(
                days=cfg.default_interval_days
            )
        else:
            # transactions are sorted by time, so the last one is the latest
            # add a millisecond to avoid retrieving it again
            transaction_time = transactions[0].time + timedelta(milliseconds=1)

        return transaction_time

    def apply_displayname_and_category(
        self, transactions: List[TransactionSchema]
    ) -> List[TransactionSchema]:
        """Process transactions and add information to them."""
        name_mapper = NameMapper(self.db)
        category_mapper = CategoryMapper(self.db)

        for transaction in transactions:
            name = transaction.counterparty.name
            transaction.counterparty.displayname = name_mapper.displayname_for(name)
            transaction.category = category_mapper.category_for(name)

        return transactions
