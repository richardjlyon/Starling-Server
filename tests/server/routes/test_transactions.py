import pytest

from tests.server.routes.test_accounts import client


@pytest.mark.skip(reason="Not implemented")
def test_transactions_account_id(account):
    response = client.get(f"/transactions/{account.uuid}")
    transactions = response.json()

    assert response.status_code == 200
    assert isinstance(transactions, list)
    assert "amount" in transactions[0]
