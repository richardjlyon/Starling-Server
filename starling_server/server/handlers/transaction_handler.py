"""
The TransactionHandler coordinates fetching new transactions from the provider, setting display name and category
information, archiving to the database, and returning to the client.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from starling_server import cfg
from starling_server.db.edgedb.database import Database
from starling_server.server.account import Account
from starling_server.server.displayname_map import DisplayNameMap
from starling_server.server.handlers.handler import Handler
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

        # Fetch new transactions from the providers
        for account in self.accounts:
            new_transactions = await get_new_transactions(self.db, account)
            insert_new_transactions(self.db, new_transactions)

        transactions = self.db.select_transactions_between(start_date, end_date)
        # processed_transactions = process_new_transactions(self.db, new_transactions)

        # sort
        pass

        return transactions


async def get_new_transactions(
    db: Database, account: Account
) -> List[TransactionSchema]:
    """Get all transactions for the account since the last recorded transaction date."""
    latest_transaction_time = get_latest_transaction_time(db, account)
    return await account.provider.get_transactions_between(
        start_date=latest_transaction_time, end_date=datetime.now()
    )


def insert_new_transactions(
    db: Database, transactions: List[TransactionSchema]
) -> None:
    """Insert new transactions into the database."""
    for transaction in transactions:
        db.upsert_transaction(transaction)


def process_new_transactions(
    db: Database,
    transactions: List[TransactionSchema],
) -> List[TransactionSchema]:
    """Process new transactions and add information to them."""
    processor = DisplayNameMap(db)

    for transaction in transactions:
        # set display name
        transaction.counterparty.displayname = processor.displayname_for(
            transaction.counterparty.name
        )

        # set category
        pass  # TODO

    return transactions


def get_latest_transaction_time(db: Database, account: Account) -> Optional[datetime]:
    """Returns the time of the latest transaction for the specified account."""

    transactions = db.select_transactions_for_account(account.schema.uuid)

    if transactions is None:
        # no transactions: compute from the default interval
        transaction_time = datetime.now() - timedelta(days=cfg.default_interval_days)
    else:
        # transactions are sorted by time, so the last one is the latest
        # add a millisecond to avoid retrieving it again
        transaction_time = transactions[0].time + timedelta(milliseconds=1)

    return transaction_time
