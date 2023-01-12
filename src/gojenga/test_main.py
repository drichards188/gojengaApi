from fastapi.testclient import TestClient

from main import app
from user.handler import UserHandler

client = TestClient(app)


def test_get_user():
    response = client.get("/user/kovax")
    assert response.status_code == 200, f'wanted 200 got {response.status_code}'
    assert response.json() == {'response': {'name': 'kovax', 'password': '5182'}}


def test_create_user():
    response = client.post("/user", json={"name": "kovax", "password": "5182"})
    assert response.json() == {"response": "insert item success"}


def test_update_user():
    response = client.put("/user/david", json={"name": "david", "password": "0000"})
    assert response.json() == {"response": "update item success"}


def test_delete_user():
    resp = UserHandler.handle_create_user('zala', '5821')
    assert resp == "insert item success"
    response = client.delete("/user/zala")
    assert response.json() == {"response": "delete item success"}