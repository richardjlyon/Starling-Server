# providers/starling/test_account_helper.py
#
# Tests the functionality of the StarlingAPI AccountHelper class
# NOTE: This operates against a live account and requires the specified bank name and account id to be present
# FIXME stub bank and account details to a fixture

from pathlib import Path

import pytest
import toml

from starling_server.providers.starling.account_helper import AccountHelper


def test_init_default():
    h = AccountHelper()
    assert isinstance(h._storage_filepath, Path)


def test_init_with_filepath(config_filepath):
    h = AccountHelper(storage_filepath=config_filepath)
    assert h._storage_filepath == config_filepath


@pytest.mark.asyncio
async def test_initialise(dummy_helper):
    # GIVEN an empty config file

    # WHEN I call "initialise()
    await dummy_helper.initialise()

    # THEN the accounts are populated from token files in the file system
    with open(dummy_helper._storage_filepath, "r") as f:
        config_file = toml.load(f)
    assert len(config_file.keys()) == 2


@pytest.mark.asyncio
async def test_register_account(
    dummy_helper, personal_account_bank_name, personal_account_id
):
    # GIVEN an empty config file

    # WHEN I add an account
    await dummy_helper.register_account(
        bank_name=personal_account_bank_name, account_uuid=personal_account_id
    )

    # THEN the config file has bank_name, token and default_category
    with open(dummy_helper._storage_filepath, "r") as f:
        config_file = toml.load(f)
    config_data = config_file[str(personal_account_id)]
    assert str(personal_account_id) in config_file
    assert config_data["account_schema"]["bank_name"] == personal_account_bank_name
    assert "token" in config_data
    assert "default_category" in config_data


@pytest.mark.asyncio
async def test_accounts(dummy_helper):
    # GIVEN an initialised helper
    await dummy_helper.initialise()

    # WHEN I get the accounts
    accounts = dummy_helper.accounts

    # THEN I get a list of AccountInfo
    assert isinstance(accounts, list)
    assert len(accounts) > 0
    assert isinstance(accounts[0], AccountHelper.AccountInfo)


@pytest.mark.asyncio
async def test_get_info_for_account_id(
    dummy_helper, personal_account_bank_name, personal_account_id
):
    # GIVEN a config file with a valid entry for an account
    await dummy_helper.register_account(
        bank_name=personal_account_bank_name, account_uuid=personal_account_id
    )

    # WHEN I get the info for the account id
    info = dummy_helper.get_info_for_account_id(account_id=personal_account_id)

    # THEN the info is returned
    assert isinstance(info, AccountHelper.AccountInfo)
    assert info.account_schema.bank_name == personal_account_bank_name
    assert isinstance(info.default_category, str)
