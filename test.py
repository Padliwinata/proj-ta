import typing
from fastapi.testclient import TestClient

from main import app
from db import db_user
import pytest
from unittest.mock import MagicMock
from fastapi import status
app.db_user = db_user

client = TestClient(app)


@pytest.fixture
def authorized_client() -> typing.Generator[TestClient, None, None]:
    client = TestClient(app)
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
    client.post('/api/register', json=test_data)
    login_data = {
        'username': 'testingusername',
        'password': 'testingpassword'
    }
    login_response = client.post('/api/auth', data=login_data)
    # print(login_response.json())
    auth_token = login_response.json()['access_token']
    client.headers.update({"Authorization": f"Bearer {auth_token}"})
    yield client
    user = db_user.fetch({'username': 'testingusername'})
    db_user.delete(user.items[0]['key'])
    


def test_register_user() -> None:
    client = TestClient(app)
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
    response = client.post('/api/register', json=test_data)
    assert response.status_code == 201
    assert response.json()['success'] is True
    user = db_user.fetch({'username': 'testingusername'})
    db_user.delete(user.items[0]['key'])


def test_register_invalid_data() -> None:
    client = TestClient(app)
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
    response = client.post('/api/register', json=invalid_user_data)
    assert response.status_code == 422
    assert 'detail' in response.json()
    assert 'value is not a valid email address' in response.json()['detail'][0]['msg']


def test_login_user(authorized_client) -> None:
    # Test case for successful user login
    test_data = {
        'username': 'testingusername',
        'password': 'testingpassword'
    }
    response = authorized_client.post('/api/auth', data=test_data)
    assert response.status_code == 200
    assert response.json()['success'] is True


def test_check_endpoint(authorized_client) -> None:
    response = authorized_client.get('/api/auth')
    print(response.json())
    assert response.status_code == 200


def test_login_user_not_found() -> None:
    # Test case for user not found scenario
    test_data = {
        'username': 'non_existent_user',
        'password': 'some_password'
    }
    response = client.post('/api/auth', data=test_data)
    assert response.status_code == 401
    assert response.json()['success'] is False
    assert response.json()['message'] == "User not found"
    
def test_login_development_mode():
    # Test case for login in development mode
    app.DEVELOPMENT = True  # Set app to development mode for this test
    test_data = {
        'username': 'alice_smith',
        'password': 'another_secure_password'
    }
    response = client.post('/api/auth', data=test_data)
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert 'access_token' in response.json()['data']  # Check if access token is returned
    app.DEVELOPMENT = False
    
# def test_login_and_upload_proof(authorized_client)-> None:
#     # Test case for successful login
#     login_data = {
#         'username': 'testingusername',
#         'password': 'testingpassword'
#     }
#     response_login = authorized_client.post('/api/auth', data=login_data)
    
#     # Assert that login is successful
#     assert response_login.status_code == 200
#     assert response_login.json()['success'] is True
#     assert 'access_token' in response_login.json()['data']

#     # Obtain access token from the login response
#     auth_token = response_login.json()['data']['access_token']

#     # Define metadata for the proof
#     metadata = {
#         'bab': '1',
#         'sub_bab': '1.1',
#         'point': 1,
#         'answer': 1,
#     }

    # # Simulate uploading a file
    # file_content = b"fake_file_content"
    # files = {'file': ("test_proof.pdf", file_content)}

    # # Send a POST request to upload the proof, including metadata and files
    # response = authorized_client.post('/api/point', files=files, data=metadata)

    # # Assert the response
    # assert response.status_code == 200
    # assert response.json()['success'] is True
    # assert response.json()['message'] == "Successfully stored"
    # assert 'data' in response.json()
    
    # # Assert that the file has been stored correctly in the database
    # assert response.json()['data']['file_name'] == f"{authorized_client.user.get_institution()['key']}_1_11_1.pdf"

def test_register_staff(authorized_client) -> None:
    # Test case for registering a new staff
    test_data = {
        'username': 'new_staff',
        'password': 'new_password',
        'email': 'staff@example.com',  # Adjusted for the required fields
        'role': 'staff'  # Adjusted for the role
    }
    response = authorized_client.post('/api/account', json=test_data)
    assert response.status_code == 201
    assert response.json()['success'] is True

# def test_register_staff_existing_user(authorized_client) -> None:
#     # Test case for registering an existing user as staff
#     test_data = {
#         'username': 'new_staff',
#         'password': 'new_password',
#         'email': 'staff@example.com',  # Adjusted for the required fields
#         'role': 'staff'
#     }
#     response = authorized_client.post('/api/account', json=test_data)
#     assert response.status_code == 400
#     assert response.json()['success'] is False
    
def test_get_login_log_as_admin(authorized_client)-> None:
    # Mocking dependencies
    authorized_client.user = MagicMock(role='admin', get_institution=MagicMock(return_value={'key': '123'}))
    mock_log_data = [
        {'name': 'Staff Name', 'email': 'staff@example.com', 'role': 'staff', 'tanggal': '2024-04-01'},
        {'name': 'Reviewer Name', 'email': 'reviewer@example.com', 'role': 'reviewer', 'tanggal': '2024-04-02'}
    ]
    authorized_client.db_user.fetch.return_value = MagicMock(count=2, items=mock_log_data)

    # Call the function
    response = authorized_client.get('/api/log')

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'message': 'Fetch Data Success',
        'success': True,
        'data': [
            {'nama': 'Staff Name', 'email': 'staff@example.com', 'role': 'staff', 'tanggal': '2024-04-01'},
            {'nama': 'Reviewer Name', 'email': 'reviewer@example.com', 'role': 'reviewer', 'tanggal': '2024-04-02'}
        ]
    }




    


