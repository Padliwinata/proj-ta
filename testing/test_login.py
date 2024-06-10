import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

def remove_access_token():
    return {"access_token": None}

def test_login_superadmin():
    response = client.post(
        "/api/auth",
        data={"username": "username", "password": "password"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "access_token" in response.json()["data"]

def test_login_admin():
    response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "access_token" in response.json()["data"]

def test_login_admin_failed():
    response = client.post(
        "/api/auth",
        data={"username": "adminnonexist", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["message"] == "User not found"

def test_login_staff():
    response = client.post(
        "/api/auth",
        data={"username": "bob_marley", "password": "yet_another_secure_password"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "access_token" in response.json()["data"]

def test_login_reviewer_internal():
    response = client.post(
        "/api/auth",
        data={"username": "emma_jones", "password": "password"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "access_token" in response.json()["data"]

def test_login_reviewer_internal_failed():
    response = client.post(
        "/api/auth",
        data={"username": "reviewerinternalnonexist", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["message"] == "User not found"

def test_login_reviewer_external():
    response = client.post(
        "/api/auth",
        data={"username": "reviewer", "password": "reviewer"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "access_token" in response.json()["data"]

def test_login_reviewer_external_failed():
    response = client.post(
        "/api/auth",
        data={"username": "reviewerexternalnonexist", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["message"] == "User not found"