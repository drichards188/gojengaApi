import unittest

from fastapi.testclient import TestClient

from decimal import *
from main import app
from handlers.user_handler import UserHandler
from handlers.account_handler import AccountHandler

client = TestClient(app)


class TestUtils(unittest.TestCase):

    def test_get_user(self):
        response = client.get("/user/kovax", headers={'Is-Test': 'True'})
        assert response.status_code == 200, f'wanted 200 got {response.status_code}'
        assert response.json() == {'response': {'name': 'kovax', 'password': '5182'}}

    def test_create_user(self):
        response = client.post("/user", json={"name": "kovax", "password": "5182"}, headers={'Is-Test': 'True'})
        assert response.json() == {'response': 'insert item succeeded'}

    def test_update_user(self):
        response = client.put("/user/david", json={"name": "david", "password": "0000"}, headers={'Is-Test': 'True'})
        assert response.json() == {"response": "update item success"}

    def test_delete_user(self):
        resp = UserHandler.handle_create_user('zala', '5821', True)
        assert resp == "insert item succeeded", 'failed to insert item before testing delete'
        response = client.delete("/user/zala", headers={'Is-Test': 'True'})
        assert response.json() == {"response": "delete item success"}

    def test_get_account(self):
        response = client.get("/account/kovax", headers={'Is-Test': 'True'})
        assert response.status_code == 200, f'wanted 200 got {response.status_code}'
        assert response.json() == {'response': {'name': 'kovax', 'balance': 235.99}}

    def test_create_account(self):
        response = client.post("/account", json={"name": "kovax", 'balance': 235.99}, headers={'Is-Test': 'True'})
        assert response.json() == {'response': 'insert item succeeded'}

    def test_update_account(self):
        response = client.put("/account/david", json={"name": "david", "balance": 235.99}, headers={'Is-Test': 'True'})
        assert response.json() == {"response": "update item success"}

    def test_delete_account(self):
        resp = AccountHandler.handle_create_account('zala', Decimal('212.38'), True)
        assert resp == "insert item succeeded", 'failed to insert item before testing delete'
        response = client.delete("/account/zala", headers={'Is-Test': 'True'})
        assert response.json() == {"response": "delete item success"}

    def test_login(self):
        response = client.post("/login", data={'username': 'zala', 'password': 'password'}, headers={'Is-Test': 'True'})
        assert response.status_code == 200, f'wanted 200 got {response.status_code}'

    def test_transaction_rollback(self):
        response = client.post("/transaction", data={
            "sender": "david",
            "receiver": "kovax2",
            "amount": 1.29
        }, headers={'Is-Test': 'True'})
        assert response.status_code == 422, f'wanted 422 got {response.status_code}'


if __name__ == '__main__':
    unittest.main()
