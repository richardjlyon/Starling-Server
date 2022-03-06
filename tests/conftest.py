import asyncio
import pytest


@pytest.fixture(scope="module")
def event_loop():
    """pytest's event-loop fixture is scoped for functions: redefine with module scope."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
