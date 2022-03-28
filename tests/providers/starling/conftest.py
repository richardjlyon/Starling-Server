# starling/conftest.py
#
# fixtures for testing the StarlingAPI class
from pathlib import Path

import pytest

from starling_server.providers.starling.api import CategoryHelper, StarlingProvider
from tests.conftest import TEST_FOLDER


@pytest.fixture()
def api_personal_account(personal_account_id):
    """Provides a StarlingAPI object initialised to the personal account."""
    return StarlingProvider(account_uuid=personal_account_id)


@pytest.fixture()
def config_filepath():
    return TEST_FOLDER / "test_config.yaml"


@pytest.fixture
def category_helper(config_filepath):
    """Create a test config file and destroy it after testing."""
    h = CategoryHelper(storage_filepath=config_filepath)
    yield h
    Path.unlink(config_filepath)


# @pytest.fixture()
# def bank_name():
#     """Retrieve a bank name from the tokens directory."""
#     bank_name = next(
#         f.name
#         for f in tokens_folder.iterdir()
#         if (f.is_file() and f.name != ".DS_Store")
#     )
#     if bank_name is None:
#         raise RuntimeError(f"No token files in {tokens_folder}")
#     return bank_name
#
#
