import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

def test_admin_registration():
    response = client.post(
        "/api/register",
        json={
            "username": "admintesting2",
            "email": "admin2@testing.com",
            "password": "password",
            "full_name": "Admin Testing",
            "role": "admin",
            "phone": "082991883774",
            "institution_name": "Admin Institution",
            "institution_address": "Jl. Pahlawan",
            "institution_phone": "082993884775",
            "institution_email": "admin@institution.com"
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"
    assert response.json()["success"] is True

def test_admin_registration_account_exist():
    response = client.post(
        "/api/register",
        json={
            "username": "admintesting2",
            "email": "admin2@testing.com",
            "password": "password",
            "full_name": "Admin Testing",
            "role": "admin",
            "phone": "082991883774",
            "institution_name": "Admin Institution",
            "institution_address": "Jl. Pahlawan",
            "institution_phone": "082993884775",
            "institution_email": "admin@institution.com"
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Username or email already"
    assert response.json()["success"] is False

