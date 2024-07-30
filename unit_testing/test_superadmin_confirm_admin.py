import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

import unittest

class TestSuperAdmin(unittest.TestCase):
    def test_admin_registration(self):
        response = client.post(
            "/api/register",
            json={
                "username": "admintesting09",
                "email": "admin09@testing.com",
                "password": "password",
                "full_name": "Admin Testing 09",
                "role": "admin",
                "phone": "0829918837749",
                "institution_name": "Admin Institution 09",
                "institution_address": "Jl. Pahlawann",
                "institution_phone": "0829938847755",
                "institution_email": "admin@institution.com"
            }
        )

        assert response.status_code == 201
        assert response.json()["message"] == "User registered successfully"
        assert response.json()["success"] is True

    def test_admin_registration_failed(self):
        response = client.post(
            "/api/register",
            json={
                "username": "admintesting09",
                "email": "admin09@testing.com",
                "password": "password",
                "full_name": "Admin Testing 09",
                "role": "admin",
                "phone": "0829918837749",
                "institution_name": "Admin Institution 09",
                "institution_address": "Jl. Pahlawann",
                "institution_phone": "0829938847755",
                "institution_email": "admin@institution.com"
            }
        )

        assert response.status_code == 400
        assert response.json()["message"] == "Username or email already exist"
        assert response.json()["success"] is False

    def test_confirm_registered_admin(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "username", "password": "password"}
        )
        access_token = login_response.json()["data"]["access_token"]
    
        user_key = "by34b8gyelfc"
        response = client.post(
            f"/api/confirm",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "key": user_key
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Confirm User Success"
        assert response.json()["success"] is True

    def test_reject_registered_admin_user_not_found(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "username", "password": "password"}
        )
        access_token = login_response.json()["data"]["access_token"]
    
        user_key = "qwx54ne2vuhda"
        response = client.delete(
            f"/api/reject",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "key": user_key
            }
        )
        assert response.status_code == 400
        assert response.json()["message"] == "User not found"
        assert response.json()["success"] is False

    def test_reject_registered_admin_success(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "username", "password": "password"}
        )
        access_token = login_response.json()["data"]["access_token"]
    
        user_key = "ajxbplnofyv4"
        response = client.delete(
            f"/api/reject",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "key": user_key
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Success altering user appearance"
        assert response.json()["success"] is True


if __name__ == "__main__":
    unittest.main()