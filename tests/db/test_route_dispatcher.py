from typing import List

import pytest

from starling_server.providers.starling.api import API as StarlingAPI
from starling_server.server.route_dispatcher import RouteDispatcher


@pytest.mark.asyncio
async def test_initialise_creates_banks_and_accounts(db):
    # GIVEN an empty database
    # WHEN I initialise an instance of RouteDispatcher
    # THEN banks and accounts are populated
    pass

    # Confirm no Accounts and Banks
    accounts_db = db.get_accounts()

    assert len(accounts_db) == 0

    # Confirm initialising RouteDispatcher populates
    banks: List[StarlingAPI] = [
        StarlingAPI(bank_name="Starling Personal"),
        StarlingAPI(bank_name="Starling Business"),
    ]
    dispatcher = RouteDispatcher(database=db, banks=banks)
    accounts_db = await dispatcher.get_accounts()

    assert len(accounts_db) > 0
