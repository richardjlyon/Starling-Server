"""
RouteDispatcher handles responding to an API call, retrieving data from account providers, storing the data, and
returning the data to the client.
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from loguru import logger

from starling_server import cfg
from starling_server.db.edgedb.database import Database
from starling_server.server.account import Account
from starling_server.server.displayname_map import DisplayNameMap
from starling_server.server.schemas import AccountSchema, TransactionSchema


class RouteDispatcher:
    """Controls server operations to coordinate fetching, storage, and publishing."""

    db: Database
    accounts: List[Account]

    def __init__(self, database: Database):
        self.db = database
        self.accounts = [
            Account(account_schema)
            for account_schema in database.select_accounts(as_schema=True)
        ]

    # = ROUTES: ACCOUNTS ===========================================================================================

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

    # = ROUTES: TRANSACTIONS =======================================================================================

    async def get_transactions_between(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[List[TransactionSchema]]:
        """Get a list of transactions between the given dates.

        This method retrieves new transactions from the providers, stores them in the database, sets each new
        transaction's counter party and category, then returns a list of transactions for the specified interval.
        """

        for account in self.accounts:
            new_transactions = await get_new_transactions(self.db, account)
            processed_transactions = process_new_transactions(self.db, new_transactions)
            insert_new_transactions(self.db, processed_transactions)

        # return transactions between the given dates
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=cfg.default_interval_days)

        return None

    # = HELPERS =======================================================================================================


async def get_new_transactions(
    db: Database, account: Account
) -> List[TransactionSchema]:
    """Get all transactions for the account since the last recorded transaction date."""

    # compute the latest transaction time for the account, or the default time interval if none
    latest_transaction_time = get_latest_transaction_time(db, account.schema.uuid)
    new_transactions = await account.provider.get_transactions_between(
        start_date=latest_transaction_time, end_date=datetime.now()
    )
    logger.info(
        f"Retrieved {len(new_transactions)} new transactions for {account.schema.account_name}"
    )
    logger.info(new_transactions)

    return new_transactions


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


def insert_new_transactions(
    db: Database, transactions: List[TransactionSchema]
) -> None:
    """Insert new transactions into the database."""
    for transaction in transactions:
        db.upsert_transaction(transaction)


def get_latest_transaction_time(
    db: Database, account_uuid: uuid.UUID
) -> Optional[datetime]:
    """Returns the time of the latest transaction for the specified account."""

    transactions = db.select_transactions_for_account(account_uuid)

    if transactions is None:
        # no transactions: compute from the default interval
        transaction_time = datetime.now() - timedelta(days=cfg.default_interval_days)
    else:
        # transactions are sorted by time, so the last one is the latest
        # add a millisecond to avoid retrieving it again
        transaction_time = transactions[0].time + timedelta(milliseconds=1)

    return transaction_time
