# server/routes/test_transactions.py
import pytest

from tests.server.routes.test_accounts import client


@pytest.mark.skip("reason=not implemented")
def test_transactions():
    # GIVEN a transactions endpoint
    # WHEN I request transactions
    response = client.get(f"/transactions")
    transactions = response.json()

    # THEN I get a list of transactions
    assert response.status_code == 200
    assert isinstance(transactions, list)
    assert "account_uuid" in transactions[0]


@pytest.mark.skip("reason=not implemented")
def test_transactions_for_account_id(config):
    # GIVEN an account uuid
    # WHEN I request transactions for that account
    response = client.get(f"/transactions/{config.account_uuid}")
    transactions = response.json()

    # THEN I get a list of transactions
    assert response.status_code == 200
    assert isinstance(transactions, list)
    assert "account_uuid" in transactions[0]
