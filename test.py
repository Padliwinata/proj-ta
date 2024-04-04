import pytest
import typing

from fastapi.testclient import TestClient

from db import db_user, db_assessment
from main import app


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
    client, _ = authorized_client
    response = client.post('/api/auth', data=test_data)
    assert response.status_code == 200
    assert response.json()['success'] is True


def test_check_endpoint(authorized_client) -> None:
    client, _ = authorized_client
    response = client.get('/api/auth')
    print(response.json())
    assert response.status_code == 200


def test_fill_assessment(authorized_client) -> None:
    client, _ = authorized_client

    client.post("/api/assessment")

    with open('Fraud D.pdf', "rb") as file:
        res = client.post('/api/point?bab=1&sub_bab=1.1&point=1&answer=1', files={'file': ("Fraud D.pdf", file, "application/pdf")})
        assert res.status_code == 200

    user = db_user.fetch({'username': 'testingusername'})
    id_user = user.items[0]['key']
    res = db_assessment.fetch({'id_admin': id_user})
    db_assessment.delete(res.items[0]['key'])


# def test_login_user_not_found() -> None:
#     # Test case for user not found scenario
#     test_data = {
#         'username': 'non_existent_user',
#         'password': 'some_password'
#     }
#     response = client.post('/api/auth', data=test_data)
#     assert response.status_code == 401
#     assert response.json()['success'] is False
#     assert response.json()['message'] == "User not found"


# def test_login_development_mode():
#     # Test case for login in development mode
#     app.DEVELOPMENT = True  # Set app to development mode for this test
#     test_data = {
#         'username': 'testingusername',
#         'password': 'testingpassword'
#     }
#     response = client.post('/api/auth', data=test_data)
#     assert response.status_code == 200
#     assert response.json()['success'] is True
#     assert 'access_token' in response.json()['data']  # Check if access token is returned
#     app.DEVELOPMENT = False


# def test_upload_proof_point_success():
#     # Simulate user authentication and obtain access token
#     access_token = create_access_token({"username": "testingusername"})
#
#     # # Test case for successful proof upload
#     # metadata = {
#     #     'bab': '1',
#     #     'sub_bab': '1.1',
#     #     'point': 1,
#     #     'answer': 1
#     # }
#     file_content = b"fake_file_content"
#     files = {'file': ("test_proof.pdf", file_content)}
#
#     # Include the access token in the request headers
#     response = client.post('/proof?bab=1&sub_bab=1.1&point=1&answer=1', headers={"Authorization": f"Bearer {access_token}"}, files=files)
#     assert response.status_code == 200
#     assert response.json()['success'] is True
#     assert response.json()['message'] == "upload berhasil"
