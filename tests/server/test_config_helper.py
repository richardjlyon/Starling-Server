import pytest

from starling_server.server.config_helper import ConfigHelper
from tests.db.database.conftest import select_accounts


@pytest.mark.asyncio
async def test_initialise_bank(empty_db, config):
    # GIVEN a configuration object with an empty database
    config_helper = ConfigHelper(empty_db)

    # WHEN I initialise a bank with a valid bank name and authorisation token
    await config_helper.initialise_bank(config.bank_name, config.token)

    # THEN the bank and account(s) are inserted in the database
    account = select_accounts(empty_db)[0]
    assert account.bank.name == config.bank_name
    assert account.name == "Personal"
