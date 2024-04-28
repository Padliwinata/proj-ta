import typing
from fastapi.testclient import TestClient


from main import app
from db import db_user, db_assessment, db_point
import pytest
from unittest.mock import MagicMock
from fastapi import status

from seeder import seed, seed_assessment


client = TestClient(app)


@pytest.fixture

def authorized_client() -> typing.Tuple[TestClient, TestClient]:
    client = TestClient(app)
    admin_client = TestClient(app)
    reviewer_client = TestClient(app)

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

    rev_data = {
        'username': 'testrev',
        'email': 'revwer@gmail.com',
        'password': 'testrev',
        'full_name': 'testing full name',
        'role': 'reviewer',
        'phone': '081357516553',
        'institution_name': 'Testing Institution',
        'institution_address': '123 Testing St',
        'institution_phone': '123456789',
        'institution_email': 'institution@example.com'
    }

    client.post('/api/register', json=test_data)
    client.post('/api/register', json=rev_data)
    login_data = {
        'username': 'testingusername',
        'password': 'testingpassword'
    }

    login_rev = {
        'username': 'testrev',
        'password': 'testrev'
    }

    login_response = client.post('/api/auth', data=login_data)
    auth_token = login_response.json()['access_token']
    admin_client.headers.update({"Authorization": f"Bearer {auth_token}"})

    login_response = client.post('/api/auth', data=login_rev)
    auth_token = login_response.json()['access_token']
    reviewer_client.headers.update({"Authorization": f"Bearer {auth_token}"})

    yield admin_client, reviewer_client

    user = db_user.fetch({'username': 'testingusername'})
    reviewer = db_user.fetch({'username': 'testrev'})
    db_user.delete(user.items[0]['key'])
    db_user.delete(reviewer.items[0]['key'])


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
    user = db_user.fetch({'username': 'testingusername'})
    db_user.delete(user.items[0]['key'])
    assert response.status_code == 201
    assert response.json()['success'] is True


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
    client, _ = authorized_client
    response = client.post('/api/auth', data=test_data)
    assert response.status_code == 200
    assert response.json()['success'] is True


def test_check_endpoint(authorized_client) -> None:
    client, _ = authorized_client
    response = client.get('/api/auth')
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


def test_register_staff(authorized_client) -> None:
    admin_client, _ = authorized_client
    test_data = {
        'username': 'new_staff',
        'password': 'new_password',
        'email': 'staff@example.com',  # Adjusted for the required fields
        'role': 'staff'  # Adjusted for the role
    }
    response = admin_client.post('/api/account', json=test_data)
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
    
# def test_get_login_log_as_admin(authorized_client)-> None:
#     # Mocking dependencies
#     authorized_client.user = MagicMock(role='admin', get_institution=MagicMock(return_value={'key': '123'}))
#     mock_log_data = [
#         {'name': 'Staff Name', 'email': 'staff@example.com', 'role': 'staff', 'tanggal': '2024-04-01'},
#         {'name': 'Reviewer Name', 'email': 'reviewer@example.com', 'role': 'reviewer', 'tanggal': '2024-04-02'}
#     ]
#     authorized_client.db_user.fetch.return_value = MagicMock(count=2, items=mock_log_data)

#     # Call the function
#     response = authorized_client.get('/api/log')

#     # Assertions
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == {
#         'message': 'Fetch Data Success',
#         'success': True,
#         'data': [
#             {'nama': 'Staff Name', 'email': 'staff@example.com', 'role': 'staff', 'tanggal': '2024-04-01'},
#             {'nama': 'Reviewer Name', 'email': 'reviewer@example.com', 'role': 'reviewer', 'tanggal': '2024-04-02'}
#         ]
#     }

def test_fill_assesment(authorized_client) -> None:
    client, _ = authorized_client

    client.post("/api/assessment")


    with open('cobafraud.pdf', "rb") as file:
        res = client.post('/api/point?bab=1&sub_bab=1.1&point=1&answer=1', files={'file': ("cobafraud.pdf", file, "application/pdf")})
        user = db_user.fetch({'username': 'testingusername'})
        id_user = user.items[0]['key']
        assessment = db_assessment.fetch({'id_admin': id_user})
        db_assessment.delete(assessment.items[0]['key'])
        assert res.status_code == 200
    
def test_start_assessment(authorized_client) -> None:
    admin_client, _ = authorized_client

    response = admin_client.post("/api/assessment")

    assert response.status_code == 201
    assert response.json()["message"] == "Start assessment success"
    assert response.json()["success"] == True
    
def test_start_assessment_existing_data(authorized_client) -> None:
    admin_client, _ = authorized_client

    # Create an existing assessment
    admin_client.post("/api/assessment")

    # Try to start assessment again
    response = admin_client.post("/api/assessment")

    assert response.status_code == 400
    assert response.json()["message"] == "Please finish last assessment first"
    assert response.json()["success"] == False

    
def test_get_all_assessment(authorized_client) -> None:
    admin_client, _ = authorized_client

    # Create an assessment
    admin_client.post("/api/assessment")

    # Get all assessments
    response = admin_client.get("/api/assessments")

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert len(response.json()["data"]) == 1  # Assuming only one assessment is created




