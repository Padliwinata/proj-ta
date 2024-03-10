from fastapi.testclient import TestClient

from main import app
from db import db_user

client = TestClient(app)

test_data = {
    'username': 'testing_username',
    'email': 'testing@gmail.com',
    'password': 'testing_password'
}


def test_register_user() -> None:
    response = client.post('/register', json=test_data)
    client.delete('/test')

    assert 'success' in response.json()
    assert response.json()['success'] is True
