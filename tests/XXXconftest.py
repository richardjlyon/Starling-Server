# import asyncio
# import uuid
# from pathlib import Path
#
# import pytest
#
# from starling_server.db.edgedb.database import Database
# from starling_server.providers.starling.account_helper import AccountHelper
# from starling_server.providers.starling.api import API as StarlingAPI
#


#
#
# @pytest.fixture()
# def test_filepath():
#     """Return the filepath of the test directory to allow temporary files to be created."""
#     return Path(__file__).parent.absolute()
#
#
# @pytest.fixture()
# def test_config_filepath(test_filepath):
#     """Return the filepath to a Starling AccountHelper config file."""
#     return test_filepath / "test_config.yaml"
#
#
# @pytest.fixture(scope="module")
# def event_loop():
#     """pytest's event-loop fixture is scoped for functions: redefine with module scope."""
#     loop = asyncio.get_event_loop()
#     yield loop
#     loop.close()
#
#
# @pytest.fixture
# def api():
#     account_uuid = uuid.UUID(personal_account.get("account_id"))
#     return StarlingAPI(account_uuid=account_uuid)
#
#
# @pytest.fixture
# async def account(api):
#     accounts = await api.get_accounts()


#     return accounts[0]
#
#
# # = DATABASE related fixtures ========================================================================================
#
# testdb = Database(database="test")
#
#
# @pytest.fixture()
# @pytest.mark.asyncio
# async def db_populated(empty_db, test_config_filepath):
#     """Returns database "test" with Starling Banks and Accounts populated from the token files."""
#
#     # build the Bank / Account configuration yaml file
#     helper = AccountHelper(storage_filepath=test_config_filepath)
#     await helper.initialise()
#
#     # populate the test database
