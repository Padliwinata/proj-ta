import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

import unittest
class TestMainPageAdmin(unittest.TestCase):
    
    def test_admin_add_staff_account(self):
        login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "John Doee",
            "role": "staff",
            "phone": "1234567890",
            "email": "john.doee@example.com",
            "username": "johndoee",
            "password": "securepasswordd"
        }
    )
        assert response.status_code == 201
        assert response.json()["success"] is True

    def test_admin_add_staff_account_exists(self):
        login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "John Doee",
            "role": "staff",
            "phone": "1234567890",
            "email": "john.doee@example.com",
            "username": "johndoee",
            "password": "securepasswordd"
        }
    )
        assert response.status_code == 400
        assert response.json()["success"] is False
        assert response.json()["message"] == "User Already Exist"

    def test_admin_add_reviewer_internal_account(self):
        login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "Reviewer Internal 3",
            "role": "reviewer",
            "phone": "12345678901",
            "email": "reviewer.internal.3@example.com",
            "username": "reviewer.internal.3",
            "password": "securepasswordd"
        }
    )
        assert response.status_code == 201
        assert response.json()["success"] is True

    def test_admin_add_reviewer_internal_account_exist(self):
        login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "Reviewer Internal 3",
            "role": "reviewer",
            "phone": "12345678901",
            "email": "reviewer.internal.3@example.com",
            "username": "reviewer.internal.3",
            "password": "securepasswordd"
        }
    )
        assert response.status_code == 400
        assert response.json()["success"] is False
        assert response.json()["message"] == "User Already Exist"

# Belum ada di sheet (-)

    def test_admin_add_staff_missing_full_name(self):
        login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "role": "staff",
            "phone": "081234567890",
            "email": "staff@example.com",
            "username": "staffuser",
            "password": "password123"
        }
    )
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Field required"
        assert response.json()["detail"][0]["loc"] == ["body", "full_name"]

    def test_admin_add_staff_missing_role(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/api/account",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "full_name": "Staff Name",
                "phone": "081234567890",
                "email": "staff@example.com",
                "username": "staffuser",
                "password": "password123"
            }
        )

        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Field required"
        assert response.json()["detail"][0]["loc"] == ["body", "role"]

    def test_admin_add_staff_missing_phone(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/api/account",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "full_name": "Staff Name",
                "role": "staff",
                "email": "staff@example.com",
                "username": "staffuser",
                "password": "password123"
            }
        )

        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Field required"
        assert response.json()["detail"][0]["loc"] == ["body", "phone"]

    def test_admin_add_staff_missing_email(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/api/account",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "full_name": "Staff Name",
                "role": "staff",
                "phone": "081234567890",
                "username": "staffuser",
                "password": "password123"
            }
        )

        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Field required"
        assert response.json()["detail"][0]["loc"] == ["body", "email"]

    def test_admin_add_staff_missing_username(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/api/account",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "full_name": "Staff Name",
                "role": "staff",
                "phone": "081234567890",
                "email": "staff@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Field required"
        assert response.json()["detail"][0]["loc"] == ["body", "username"]

    def test_admin_add_staff_missing_password(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/api/account",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "full_name": "Staff Name",
                "role": "staff",
                "phone": "081234567890",
                "email": "staff@example.com",
                "username": "staffuser"
            }
        )

        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Field required"
        assert response.json()["detail"][0]["loc"] == ["body", "password"]
        
            
if __name__ == "__main__":
    unittest.main()