"""
RouteDispatcher handles responding to an API call, retrieving data from account providers, storing the data, and
returning the data to the client.
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from starling_server import cfg
from starling_server.db.edgedb.database import Database
from starling_server.server.account import Account
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

        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=cfg.default_interval_days)

        # calls = [
        #     account.provider.get_transactions_between(start_date, end_date)
        #     for account in self.accounts
        # ]
        # transactions = await asyncio.gather(*calls)
        # transactions = list(itertools.chain(*transactions))
        # transactions.sort(key=lambda t: t.time, reverse=True)

        new_transactions = await get_new_transactions(self.accounts, self.db)
        # processed_transactions = insert_transaction_information(
        #     self.db, new_transactions
        # )
        # return processed_transactions_between(self.db, start_date, end_date)

        return new_transactions

    async def get_transactions_for_account_id_between(
        self,
        account_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[List[TransactionSchema]]:
        """Get transactions for the specified account for the default time interval."""

        # FIXME Tidy this logic up include start_date OR end_date
        # TODO start_date is earliest of (start_date / account_last_updated)
        if start_date or end_date is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=cfg.default_interval_days)

        # get latest transactions
        # provider = self.get_provider_for_id(account_id)
        # transactions = await provider.get_transactions_between(start_date, end_date)
        #
        # # save to the database
        # for transaction in transactions:
        #     # counter_party = make_counterparty_from(transaction)
        #     self.db.upsert_transaction(transaction)
        #
        # return transactions

        # = HELPERS =======================================================================================================


def get_latest_transaction_time(db: Database, account_uuid: uuid.UUID) -> datetime:
    """Returns the time of the latest transaction for the specified account."""
    pass


async def get_new_transactions(
    accounts: List[Account], db: Database
) -> List[TransactionSchema]:
    """Get all transactions from each provider since the last recorded transaction date."""
    transactions = []
    for account in accounts:
        # compute the last transaction time for account
        latest_transaction_time = get_latest_transaction_time(db, account.schema.uuid)

        # fetch new transactions
        transactions.extend(
            account.provider.get_transactions_between(
                start_date=latest_transaction_time, end_date=datetime.now()
            )
        )

    return transactions
