import asyncio
import itertools
import uuid
from datetime import datetime
from typing import List, Optional

from starling_server.providers.provider import Provider
from starling_server.server.schemas import AccountSchema, TransactionSchema


class TransactionFetcher:
    """
    TransactionFetcher is responsible for retrieving transactions from an account provider.
    """

    def __init__(self, accounts: List[AccountSchema], providers: List[Provider]):
        self.accounts = accounts
        self.providers = providers

    def get_provider_for_account_uuid(
        self, account_uuid: uuid.UUID
    ) -> Optional[Provider]:
        """Returns the account with the given id, or None."""
        return next(
            provider
            for provider in self.providers
            if provider.account_uuid == account_uuid
        )

    async def fetch(
        self, start_date: datetime, end_date: datetime
    ) -> List[TransactionSchema]:
        """
        Fetches transactions from the account provider.
        Returns:
             A list of transactions sorted by date.
        """
        calls = [
            provider.get_transactions_between(start_date, end_date)
            for provider in self.providers
        ]
        transactions = await asyncio.gather(*calls)
        transactions = list(itertools.chain(*transactions))
        transactions.sort(key=lambda t: t.time, reverse=True)
        return transactions
