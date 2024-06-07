import typing
from fastapi.testclient import TestClient


from main import app
from db import db_user, db_assessment, db_point
import pytest
from unittest.mock import MagicMock
from fastapi import status

from seeder import seed, seed_assessment


@pytest.fixture
def authorized_client() -> typing.Generator[typing.Tuple[TestClient, TestClient, TestClient], None, None]:
    client = TestClient(app)
    admin_client = TestClient(app)
    reviewer_client = TestClient(app)
    staff_client = TestClient(app)
    # super_admin_client = TestClient(app)

    test_data = {
        'username': 'testingusername',
        'email': 'testing@gmail.com',
        'password': 'testingpassword',
        'full_name': 'testing full name',
        'role': 'admin',
        'phone': '081357516553',
        'id_institution': "gc8uupscjs0e",
        'is_active': True,
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
    staff_data = {
        'username': 'staffbaruaja',
        'email': 'staffbaruaja@gmail.com',
        'password': 'staffbaruaja',
        'full_name': 'testing staff',
        'role': 'staff',
        'phone': '081999000222',
        'institution_name': 'Testing Institution',
        'institution_address': '123 Testing St',
        'institution_phone': '123456789',
        'institution_email': 'institution@example.com'
    }

    client.post('/api/register', json=test_data)
    client.post('/api/register', json=rev_data)
    staff_response = client.post('/api/register', json=staff_data)
    print(staff_response.json())
    login_data = {
        'username': 'testingusername',
        'password': 'testingpassword'
    }
    login_rev = {
        'username': 'testrev',
        'password': 'testrev'
    }
    login_staff = {
        'username': 'staffbaruaja',
        'password': 'staffbaruaja'

    }
    login_response = client.post('/api/auth', data=login_data)
    auth_token = login_response.json()['access_token']
    admin_client.headers.update({"Authorization": f"Bearer {auth_token}"})

    login_response = client.post('/api/auth', data=login_rev)
    auth_token = login_response.json()['access_token']
    reviewer_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    
    login_response = client.post('/api/auth', data=login_staff)
    auth_token = login_response.json()['access_token']
    staff_client.headers.update({"Authorization": f"Bearer {auth_token}"})

    yield admin_client, reviewer_client, staff_client

    user = db_user.fetch({'username': 'testingusername'})
    reviewer = db_user.fetch({'username': 'testrev'})
    staff = db_user.fetch({'username': 'teststaff'})
    print(staff.items)
    db_user.delete(user.items[0]['key'])
    db_user.delete(reviewer.items[0]['key'])
    db_user.delete(staff.items[0]['key'])


def test_register_admin() -> None:
    client = TestClient(app)
    test_data = {
        'username': 'testingusername',
        'email': 'testing@gmail.com',
        'password': 'testingpassword',
        'full_name': 'testing full name',
        'role': 'admin',
        'phone': '081357516553',
        'id_institution': "gc8uupscjs0e",
        'is_active': True,
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
        'institution_email': 'institutionexamplecom'  # invalid email format
    }
    response = client.post('/api/register', json=invalid_user_data)
    assert response.status_code == 422
    assert 'detail' in response.json()
    assert 'value is not a valid email address' in response.json()['detail'][0]['msg']


def test_login_admin(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    # Test case for successful user login
    test_data = {
        'is_active': "true",
        'username': 'testingusername',
        'password': 'testingpassword'
    }
    admin_client, _, _ = authorized_client
    response = admin_client.post('/api/auth', data=test_data)
    assert response.status_code == 200
    assert response.json()['success'] is True

def test_login_staff(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    # Test case for successful user login
    test_data = {
        'username': 'teststaff',
        'password': 'teststaff'
    }
    _, _, staff_client = authorized_client
    response = staff_client.post('/api/auth', data=test_data)
    assert response.status_code == 200
    assert response.json()['success'] is True


def test_check_endpoint(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    client, _, _ = authorized_client
    response = client.get('/api/auth')
    print(response.json())
    assert response.status_code == 200


def test_login_admin_not_found() -> None:
    client = TestClient(app)
    # Test case for user not found scenario
    test_data = {
        'username': 'non_existent_user',
        'password': 'some_password'
    }
    response = client.post('/api/auth', data=test_data)
    assert response.status_code == 401
    assert response.json()['success'] is False
    assert response.json()['message'] == "User not found"


def test_register_reviewer() -> None:
    client = TestClient(app)
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
    response = client.post('/api/register', json=rev_data)
    user = db_user.fetch({'username': 'testrev'})
    db_user.delete(user.items[0]['key'])
    assert response.status_code == 201
    assert response.json()['success'] is True


def test_register_reviewer_invalid_data() -> None:
    client = TestClient(app)
    # Test case for registering a user with invalid data
    invalid_rev_data = {
        'username': 'testrev',
        'email': 'revwer@gmail.com',
        'password': 'testrev',
        'full_name': 'testing full name',
        'role': 'reviewer',
        'phone': '081357516553',
        'institution_name': 'Testing Institution',
        'institution_address': '123 Testing St',
        'institution_phone': '123456789',
        'institution_email': 'institutionexamplecom' #invalid email  format
    }
    response = client.post('/api/register', json=invalid_rev_data)
    assert response.status_code == 422
    assert 'detail' in response.json()
    assert 'value is not a valid email address' in response.json()['detail'][0]['msg']


def test_login_reviewer(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    # Test case for successful user login
    rev_data = {
        'username': 'testrev',
        'password': 'testrev'
    }
    _, client, _ = authorized_client
    response = client.post('/api/auth', data=rev_data)
    assert response.status_code == 200
    assert response.json()['success'] is True
    

def test_login_rev_not_found() -> None:
    client = TestClient(app)
    # Test case for user not found scenario
    rev_data = {
        'username': 'non_existent_rev',
        'password': 'some_password'
    }
    response = client.post('/api/auth', data=rev_data)
    assert response.status_code == 401
    assert response.json()['success'] is False
    assert response.json()['message'] == "User not found"


def test_register_staff(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    admin_client, _, _ = authorized_client
    
    # Data untuk pendaftaran staf baru
    test_data = {
        'full_name': 'Testing Staff',
        'role': 'staff',
        'phone': '093748499',
        'email': 'staff@gmail.com',
        'username': 'staff_yuna',
        'password': 'stafyuna'
    }
    
    # Panggil endpoint untuk pendaftaran staf baru
    response = admin_client.post('/api/account', json=test_data)
    
    # Periksa apakah pendaftaran berhasil
    assert response.status_code == 201  # Periksa status kode 201 Created
    assert response.json()['success'] is True  # Pastikan bahwa pendaftaran berhasil


def test_register_existing_user(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    admin_client, _, _ = authorized_client
    
    # Data untuk pengguna yang sudah terdaftar sebelumnya
    test_data = {
        'full_name': 'Testing Staff',
        'role': 'staff',
        'phone': '093748499',
        'email': 'staff@gmail.com',
        'username': 'staff_yuna',
        'password': 'stafyuna'
    }

    # Menambahkan pengguna yang sudah terdaftar sebelumnya ke database
    db_user.put(test_data)

    # Panggil endpoint untuk pendaftaran pengguna yang sama
    response = admin_client.post('/api/account', json=test_data)
    
    # Periksa apakah pendaftaran gagal karena pengguna sudah terdaftar sebelumnya
    assert response.status_code == 400  # Periksa status kode 400 Bad Request
    assert response.json()['success'] is False  # Pastikan bahwa pendaftaran gagal
    assert response.json()['message'] == "User Already Exist"  # Pastikan bahwa pesan yang tepat dikembalikan oleh endpoint


def test_login_staff_not_found() -> None:
    client = TestClient(app)
    # Test case for user not found scenario
    test_data = {
        'username': 'non_existent_staff',
        'password': 'some_password'
    }
    response = client.post('/api/auth', data=test_data)
    assert response.status_code == 401
    assert response.json()['success'] is False
    assert response.json()['message'] == "User not found"


def test_fill_assessment(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    admin_client, _, _ = authorized_client
    with open('cobafraud.pdf', "rb") as file:
        res = admin_client.post('/api/point?bab=1&sub_bab=1.1&point=1&answer=1', files={'file': ("cobafraud.pdf", file, "application/pdf")})
        user = db_user.fetch({'username': 'testingusername'})
        id_user = user.items[0]['key']
        assessment = db_assessment.fetch({'id_admin': id_user})
        db_assessment.delete(assessment.items[0]['key'])
        assert res.status_code == 200


def test_start_assessment(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    admin_client, _, _ = authorized_client

    response = admin_client.post("/api/assessment")

    assert response.status_code == 201
    assert response.json()["message"] == "Start assessment success"
    assert response.json()["success"] == True


def test_start_assessment_existing_data(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    admin_client, _, _ = authorized_client

    # Create an existing assessment
    admin_client.post("/api/assessment")

    # Try to start assessment again
    response = admin_client.post("/api/assessment")

    assert response.status_code == 400
    assert response.json()["message"] == "Please finish last assessment first"
    assert response.json()["success"] == False

    
def test_get_all_assessment(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    admin_client, _, _ = authorized_client

    # Create an assessment
    admin_client.post("/api/assessment")

    # Get all assessments
    response = admin_client.get("/api/assessments")

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert len(response.json()["data"]) == 1  # Assuming only one assessment is created


def test_get_finished_assessments_with_assessment(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    admin_client, _, _ = authorized_client
    
    # Create an ongoing assessment
    admin_client.post("/api/assessment")
    
    # Call the endpoint
    response = admin_client.get("/api/assessments/progress")
    
    # Assert the response
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] == True


def test_get_finished_assessments_no_assessment(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    admin_client, _, _ = authorized_client
    
    # Call the endpoint
    response = admin_client.get("/api/assessments/progress")
    
    # Assert the response
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["success"] == False
    assert response.json()["message"] == "Assessment not found"


def test_start_evaluation_not_reviewer(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    admin_client, _, _ = authorized_client

    # Kirim permintaan untuk memulai evaluasi oleh reviewer internal
    response = admin_client.get("/api/assessments/evaluation?id_assessment=1234")

    # Periksa apakah permintaan berhasil
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["success"] == False
    assert response.json()["message"] == "Forbidden access"


def test_start_evaluation_internal_reviewer(authorized_client: typing.Tuple[TestClient, TestClient, TestClient]) -> None:
    _, reviewer_client, _ = authorized_client

    # Kirim permintaan untuk memulai evaluasi oleh reviewer eksternal
    response = reviewer_client.get("/api/assessments/evaluation?id_assessment=sdhjsjd")

    # Periksa apakah permintaan berhasil
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] == True
    assert response.json()["message"] == "Start reviewing success"
    
