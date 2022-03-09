import asyncio
import pytest

from starling_server.providers.starling.api import API as StarlingAPI


@pytest.fixture(scope="module")
def event_loop():
    """pytest's event-loop fixture is scoped for functions: redefine with module scope."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def api():
    return StarlingAPI(bank_name="Starling Personal")


@pytest.fixture
async def account(api):
    accounts = await api.get_accounts()
    return accounts[0]
