from fastapi.testclient import TestClient

from server.app import app

client = TestClient(app)


class TestAccounts:
    def test_accounts(self):
        response = client.get("/accounts")
        data = response.json()

        assert response.status_code == 200
        assert isinstance(data, list)
        assert "accounts" in data[0]
