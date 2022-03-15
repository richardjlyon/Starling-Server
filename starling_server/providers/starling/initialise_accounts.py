# providers/starling/initialise_accounts.py
#
# Utility script to initialise AccountHelper with accounts authorised with tokens
#
# This has to be run each time a new Starling Bank and/or new Starling account is added to ensure
# that the default category is recorded for API calls

# FIXME Add this to the command line utility as a custom task when adding starling accounts.

import asyncio

from loguru import logger

from starling_server.main import db
from starling_server.providers.starling.api_v2 import CategoryHelper


async def initialise_config():
    query = db.client.query(
        """
        select Bank {
            auth_token_hash,
            accounts: { uuid }
        }
        """
    )

    helper = CategoryHelper()
    account_count = 0
    for bank in query:
        token = bank.auth_token_hash
        for account in bank.accounts:
            account_uuid = account.uuid
            await helper.insert(token, account_uuid)
            account_count += 1

    logger.info(
        "Added {} accounts in config file {}", account_count, helper._storage_filepath
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialise_config())
