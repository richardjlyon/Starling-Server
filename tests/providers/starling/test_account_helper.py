# test_account_helper.py
#
# Tests the functionality of the StarlingAPI AccountHelper class
# NOTE: This operates against a live account and requires the specified bank name and account id to be present
# FIXME stub bank and account details to a fixture

import uuid
from pathlib import Path

import pytest
import toml

from starling_server.providers.starling.account_helper import AccountHelper


def test_initialise_default():
    h = AccountHelper()
    assert isinstance(h._filepath, Path)


def test_initialise_with_filepath(helper):
    assert isinstance(helper._filepath, Path)


@pytest.mark.asyncio
async def test_register_account(helper):
    # GIVEN an empty config file
    # WHEN I add an account
    # THEN the config file has bank_name, token and default_category

    bank_name = "Starling Business"
    account_uuid = uuid.UUID("7327c655-31f6-4f21-ac8e-74880e5c8a47")
    await helper.register_account(bank_name=bank_name, account_uuid=account_uuid)
    # load the the config yaml file
    with open(helper._filepath, "r") as f:
        config_file = toml.load(f)

    assert str(account_uuid) in config_file

    config_data = config_file[str(account_uuid)]
    assert config_data["bank_name"] == bank_name
    assert "token" in config_data
    assert "default_category" in config_data


@pytest.mark.asyncio
async def test_get_for_account_id(helper):
    # GIVEN a config file with a valid entry for an account
    # WHEN I get the info for the account id
    # the info is returned

    # add an account
    helper = helper
    bank_name = "Starling Business"
    account_uuid = uuid.UUID("7327c655-31f6-4f21-ac8e-74880e5c8a47")
    await helper.register_account(bank_name=bank_name, account_uuid=account_uuid)

    # get the info
    info = helper.get_for_account_id(account_id=account_uuid)
    assert isinstance(info, AccountHelper.AccountInfo)
    assert info.bank_name == bank_name
    assert isinstance(info.default_category, uuid.UUID)
