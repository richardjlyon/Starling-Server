from tests.server.routes.test_accounts import client


def test_transactions_for_account_id(account):
    response = client.get(f"/transactions/{account.uuid}")
    transactions = response.json()

    assert response.status_code == 200
    assert isinstance(transactions, list)
    assert "account_uuid" in transactions[0]
