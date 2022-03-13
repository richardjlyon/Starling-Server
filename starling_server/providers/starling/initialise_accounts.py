# providers/starling/initialise_accounts.py
#
# utility script to initialise AccountHelper with accounts authorised with tokens

import asyncio

from loguru import logger

from starling_server.providers.starling.account_helper import AccountHelper


async def initialise_config():
    h = AccountHelper()
    accounts_added = await h.initialise()
    logger.info("Initialised. Added {} accounts", accounts_added)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialise_config())
