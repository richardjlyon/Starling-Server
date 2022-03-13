from pathlib import Path

import pytest

from starling_server.config import tokens_folder
from starling_server.providers.starling.account_helper import AccountHelper


@pytest.fixture()
def bank_name():
    """Retrieve a bank name from the tokens directory."""
    bank_name = next(
        f.name
        for f in tokens_folder.iterdir()
        if (f.is_file() and f.name != ".DS_Store")
    )
    if bank_name is None:
        raise RuntimeError(f"No token files in {tokens_folder}")
    return bank_name


@pytest.fixture
def helper():
    """Create a test config file and destroy it after testing."""
    filepath = Path(__file__).parent.absolute()
    temp_config = filepath / "temp.yaml"

    h = AccountHelper(temp_config)

    yield h

    Path.unlink(temp_config)
