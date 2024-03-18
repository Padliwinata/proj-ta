from fastapi.testclient import TestClient

from main import app
from db import db_user


client = TestClient(app)


def test_register_user() -> None:
    # Test case for user registration
    test_data = {
        'username': 'testing_username',
        'email': 'testing@gmail.com',
        'password': 'testing_password'
    }

    # Test with valid data
    response = client.post('/register', json=test_data)
    if response.status_code == 200 and response.json()['success'] is True:
        print("Registration successful.")
        client.delete('/test')
    else:
        print("Invalid data. Registration failed.")

    # Test with invalid data
def test_register_invalid_data() -> None:
    # Test case for registering a user with invalid data
    invalid_user_data = {
        'username': 'yuna',  
        'email': 'invalid_email',  # Invalid email format
        'password': 'paswordyuna' 
    }
    response = client.post('/register', json=invalid_user_data)
    
    if response.status_code == 422 and 'detail' in response.json() and 'validation error' in response.json()['detail'][0]['msg']:
        print("Email not valid.")
    else:
        print("registration successful.")

def test_login_user() -> None:
    # Test case for user login
    test_data = {
        'username': 'testing_username',
        'password': 'testing_password'
    }

    # Test with valid login credentials
    response = client.post('/login', json=test_data)
    if response.status_code == 200 and response.json()['success'] is True:
        print("Login successful.")
    else:
        print("Invalid login credentials. Login failed.")

    # Test with invalid login credentials
def test_login_invalid_credentials() -> None:
    # Test case for login with invalid credentials
    invalid_login_data = {
        'username': 'invalid_username',
        'password': 'invalid_password'
    }

    response = client.post('/login', json=invalid_login_data)
    
    if response.status_code == 401 and 'detail' in response.json() and 'Invalid credentials' in response.json()['detail']:
        print("Invalid login credentials.")
       
    else:
        print("Login successful.")
        



    

