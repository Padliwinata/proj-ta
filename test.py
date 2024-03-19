from fastapi.testclient import TestClient

from main import app
from db import db_user


client = TestClient(app)
    

def test_register_user() -> None:
    # Test case for successful user registration
    test_data = {
        'username': 'testing_username',
        'email': 'testing@gmail.com',
        'password': 'testing_password'
    }
    response = client.post('/register', json=test_data)
    assert response.status_code == 200
    assert response.json()['success'] is True



def test_register_invalid_data() -> None:
    # Test case for registering a user with invalid data
    invalid_user_data = {
        'username': 'yuna',  
        'email': 'invalid_email',  # Invalid email format
        'password': 'paswordyuna' 
    }
    response = client.post('/register', json=invalid_user_data)
    assert response.status_code == 422  
    assert 'detail' in response.json()
    assert 'value is not a valid email address' in response.json()['detail'][0]['msg']
    
def test_login_user() -> None:
    # Test case for user login
    test_data = {
        'username': 'testing_username',
        'password': 'testing_password'
    }

    # Test with valid login credentials
    response = client.post('/login', json=test_data)
    assert response.status_code == 200 and response.json()['success'] is True
    # Additional actions for successful login, if needed



