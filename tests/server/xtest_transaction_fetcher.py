from datetime import datetime, timedelta

import pytest

from starling_server.providers.starling.api import StarlingProvider
from starling_server.server.schemas import TransactionSchema
from starling_server.server.transaction_fetcher import TransactionFetcher


def test_init(testdb_with_real_accounts):
    accounts = testdb_with_real_accounts.select_accounts(as_schema=True)
    providers = provider_factory(testdb_with_real_accounts)
    tf = TransactionFetcher(accounts=accounts, providers=providers)
    assert tf.accounts == accounts
    assert tf.providers == providers
    print(accounts[0])


def test_get_provider_for_account_uuid(testdb_with_real_accounts):
    # GIVEN a test database populated with accounts and a transaction fetcher
    accounts = testdb_with_real_accounts.select_accounts(as_schema=True)
    providers = provider_factory(testdb_with_real_accounts)
    tf = TransactionFetcher(accounts=accounts, providers=providers)

    # WHEN I get the provider class for the firsst account
    provider = tf.get_provider_for_account_uuid(accounts[0].uuid)

    # THEN the correct provider class is returned
    assert isinstance(provider, StarlingProvider)


@pytest.mark.asyncio
async def test_fetch(testdb_with_real_accounts):
    # GIVEN a transaction fetcher
    accounts = testdb_with_real_accounts.select_accounts(as_schema=True)
    providers = provider_factory(testdb_with_real_accounts)
    tf = TransactionFetcher(accounts=accounts, providers=providers)

    # WHEN I fetch transactions for all accounts for the last 14 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)
    transactions = await tf.fetch(start_date, end_date)

    # THEN transactions for all accounts are returned, sorted by date
    assert isinstance(transactions, list)
    assert isinstance(transactions[0], TransactionSchema)
    assert transactions[0].time > transactions[-1].time
