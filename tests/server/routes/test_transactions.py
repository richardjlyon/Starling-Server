# server/routes/test_transactions.py

from tests.server.routes.test_accounts import client


def test_transactions_for_account_id(config):
    response = client.get(f"/transactions/{config.account_uuid}")
    transactions = response.json()

    assert response.status_code == 200
    assert isinstance(transactions, list)
    assert "account_uuid" in transactions[0]


def test_transactions():
    response = client.get(f"/transactions")
    transactions = response.json()

    assert response.status_code == 200
    assert isinstance(transactions, list)
    assert "account_uuid" in transactions[0]
