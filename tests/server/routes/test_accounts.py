"""
Tests the functionality of the FastAPI routes.
These tests require Accounts to be present in the live database
# FIXME rewrite tests to use mocking
"""

from fastapi.testclient import TestClient

from starling_server.app import app

client = TestClient(app)


def test_accounts():
    response = client.get("/accounts")
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert "uuid" in data[0]


def test_accounts_balance():
    response = client.get("/accounts/balances")
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert "cleared_balance" in data[0]
