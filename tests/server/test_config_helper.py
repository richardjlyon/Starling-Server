import pytest

from starling_server.server.config_helper import ConfigHelper
from tests.conftest import select_accounts


@pytest.mark.asyncio
async def test_initialise_bank(empty_db, personal_auth_token):
    # GIVEN a configuration object with an empty database
    config = ConfigHelper(db=empty_db)

    # WHEN I initialise a bank with a valid bank name and authorisation token
    await config.initialise_bank("Starling Personal", personal_auth_token)

    # THEN the bank and account(s) are inserted in the database
    account = select_accounts()[0]
    assert account.bank.name == "Starling Personal"
    assert account.name == "Personal"
