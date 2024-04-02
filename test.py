from fastapi.testclient import TestClient

from dependencies import create_access_token
from main import app
from db import db_user


client = TestClient(app)
    

def test_register_user():
    test_data = {
        'username': 'testingusername',
        'email': 'testing@gmail.com',
        'password': 'testingpassword',
        'full_name': 'testing full name',
        'role': 'admin',
        'phone': '081357516553',
        'institution_name': 'Testing Institution',
        'institution_address': '123 Testing St',
        'institution_phone': '123456789',
        'institution_email': 'institution@example.com'
    }
    response = client.post('/register', json=test_data)
    assert response.status_code == 201
    assert response.json()['success'] is True


def test_register_invalid_data() -> None:
    # Test case for registering a user with invalid data
    invalid_user_data = {
        'username': 'testingusername',
        'email': 'testing@gmail.com',
        'password': 'testingpassword',
        'full_name': 'testing full name',
        'role': 'admin',
        'phone': '081357516553',
        'institution_name': 'Testing Institution',
        'institution_address': '123 Testing St',
        'institution_phone': '123456789',
        'institution_email': 'institutionexamplecom' #invalid email  format
    }
    response = client.post('/register', json=invalid_user_data)
    assert response.status_code == 422  
    assert 'detail' in response.json()
    assert 'value is not a valid email address' in response.json()['detail'][0]['msg']
    
def test_login_user() -> None:
    # Test case for successful user login
    test_data = {
        'username': 'testingusername',
        'password': 'testingpassword'
    }
    response = client.post('/auth', data=test_data)
    assert response.status_code == 200
    assert response.json()['success'] is True

def test_login_user_not_found() -> None:
    # Test case for user not found scenario
    test_data = {
        'username': 'non_existent_user',
        'password': 'some_password'
    }
    response = client.post('/auth', data=test_data)
    assert response.status_code == 401
    assert response.json()['success'] is False
    assert response.json()['message'] == "User not found"
    
def test_login_development_mode():
    # Test case for login in development mode
    app.DEVELOPMENT = True  # Set app to development mode for this test
    test_data = {
        'username': 'testingusername',
        'password': 'testingpassword'
    }
    response = client.post('/auth', data=test_data)
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert 'access_token' in response.json()['data']  # Check if access token is returned
    app.DEVELOPMENT = False
    
def test_upload_proof_point_success():
    # Simulate user authentication and obtain access token
    test_data = {
        'username': 'testingusername',
        'password': 'testingpassword'
    }
    response = client.post('/auth', data=test_data)
    access_token = response.json()['data']['access_token']
    
    print(access_token)

    # # Test case for successful proof upload
    # metadata = {
    #     'bab': '1',
    #     'sub_bab': '1.1',
    #     'point': 1,
    #     'answer': 1
    # }
    file_content = b"fake_file_content"
    files = {'file': ("test_proof.pdf", file_content)}

    # Include the access token in the request headers
    response = client.post('/proof?bab=1&sub_bab=1.1&point=1&answer=1', headers={"Authorization": f"Bearer {access_token}"}, files=files)
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert response.json()['message'] == "upload berhasil"
