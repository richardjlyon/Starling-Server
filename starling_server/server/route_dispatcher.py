"""
RouteDispatcher handles responding to an API call, retrieving data from account providers, storing the data, and
returning the data to the client.
"""
import asyncio
import importlib
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from starling_server import cfg
from starling_server.db.edgedb.database import Database
from starling_server.providers.provider_api import ProviderAPI
from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema


class RouteDispatcher:
    """Controls server operations to coordinate fetching, storage, and publishing."""

    db: Database
    providers: List[ProviderAPI]

    def __init__(self, database: Database):
        self.db = database
        self.providers = provider_factory(database)

    # = ROUTES: ACCOUNTS ===============================================================================================

    async def get_accounts(self) -> List[AccountSchema]:
        """Get a list of accounts from the database.

        Args:
            force_refresh (bool): If true, force update of account details from the provider

        Returns:
            A list of `AccountSchema` objects
        """
        return self.db.select_accounts(as_schema=True)

    async def get_account_balances(
        self,
    ):
        """Get a list of account balances from the providers."""
        return await asyncio.gather(
            *[provider.get_account_balance() for provider in self.providers]
        )

    # = ROUTES: TRANSACTIONS ===========================================================================================

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
        provider = self.get_provider_for_id(account_id)
        transactions = await provider.get_transactions_between(start_date, end_date)

        # save to the database
        for transaction in transactions:
            # counter_party = make_counterparty_from(transaction)
            self.db.upsert_transaction(transaction)

        return transactions

    async def get_transactions_between(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Optional[List[TransactionSchema]]:

        transactions = []
        for account in self.db.select_accounts(as_schema=True):
            result = await self.get_transactions_for_account_id_between(
                account_id=account.uuid, start_date=start_date, end_date=end_date
            )
            transactions.extend(result)

        transactions.sort(key=lambda t: t.time, reverse=True)
        return transactions

    # = HELPERS =======================================================================================================

    def get_provider_for_id(self, account_uuid: uuid.UUID) -> Optional[ProviderAPI]:
        """Returns the account with the given id, or None."""
        return next(
            provider
            for provider in self.providers
            if provider.account_uuid == account_uuid
        )


def provider_factory(database: Database) -> List[ProviderAPI]:
    """Returns a list of provider api objects for each bank in the database."""
    banks_db = database.client.query(
        """
        select Bank {
            name,
            auth_token_hash,
            accounts: {
                uuid
            }
        }
        """
    )

    provider_list = []
    for bank in banks_db:
        for account in bank.accounts:
            provider: ProviderAPI = get_provider_for_bank_name(bank.name)
            provider_list.append(
                provider(
                    auth_token=bank.auth_token_hash,
                    account_uuid=account.uuid,
                    bank_name=bank.name,
                )
            )

    return provider_list


def get_provider_for_bank_name(bank_name) -> ProviderAPI:
    """Returns a provider class computed from bank_name"""
    api_class = cfg.bank_classes.get(bank_name)
    module = importlib.import_module(f"starling_server.providers.{api_class}.api")
    class_ = getattr(module, "Starling_API")
    return class_
