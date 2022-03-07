import pytest

from providers.starling.api import API as StarlingAPI


@pytest.fixture
def api():
    return StarlingAPI(bank_name="personal")


@pytest.fixture
async def account(api):
    accounts = await api.get_accounts()
    return accounts[0]
