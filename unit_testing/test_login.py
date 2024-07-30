import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app
from html_reporter import HTMLTestRunner

client = TestClient(app)

import unittest
class TestLogin(unittest.TestCase):
    def remove_access_token(self):
        return {"access_token": None}

    def test_login_superadmin(self):
        response = client.post(
        "/api/auth",
        data={"username": "username", "password": "password"}
    )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "access_token" in response.json()["data"]
        
    def test_login_superadmin_failed(self):
        response = client.post(
        "/api/auth",
        data={"username": "superadminnonexist", "password": "wrongpassword"}
    )
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert response.json()["message"] == "User not found"

    def test_login_admin(self):
        response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "access_token" in response.json()["data"]

    def test_login_admin_failed(self):
        response = client.post(
        "/api/auth",
        data={"username": "adminnonexist", "password": "wrongpassword"}
    )
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert response.json()["message"] == "User not found"

    def test_login_staff(self):
        response = client.post(
        "/api/auth",
        data={"username": "staff_perusahaan", "password": "password_baru"}
    )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "access_token" in response.json()["data"]
        
    def test_login_staff_failed(self):
        response = client.post(
        "/api/auth",
        data={"username": "staffnonexist", "password": "wrongpassword"}
    )
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert response.json()["message"] == "User not found"

    def test_login_reviewer_internal(self):
        response = client.post(
        "/api/auth",
        data={"username": "emma_jones", "password": "password"}
    )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "access_token" in response.json()["data"]

    def test_login_reviewer_internal_failed(self):
        response = client.post(
        "/api/auth",
        data={"username": "reviewerinternalnonexist", "password": "wrongpassword"}
    )
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert response.json()["message"] == "User not found"

    def test_login_reviewer_external(self):
        response = client.post(
        "/api/auth",
        data={"username": "reviewer", "password": "reviewer"}
    )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "access_token" in response.json()["data"]

    def test_login_reviewer_external_failed(self):
        response = client.post(
        "/api/auth",
        data={"username": "reviewerexternalnonexist", "password": "wrongpassword"}
    )
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert response.json()["message"] == "User not found"
        
if __name__ == "__main__":
    runner = HTMLTestRunner(
        report_filepath="my_report.html",
        title="Test Login",
        description="Ini test login",
        open_in_browser=True
    )

    # run the test
    unittest.main(testRunner=runner)