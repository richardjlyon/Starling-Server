from fastapi.testclient import TestClient

from server.app import app

client = TestClient(app)


class TestAccounts:
    def test_accounts(self):
        response = client.get("/accounts")
        data = response.json()

        assert response.status_code == 200
        assert isinstance(data, list)
        assert "uuid" in data[0]

    def test_accounts_balance(self):
        response = client.get("/accounts/balances")
        data = response.json()

        assert response.status_code == 200
        assert isinstance(data, list)
        assert "cleared_balance" in data[0]