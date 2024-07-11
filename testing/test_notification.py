import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json

from fastapi.testclient import TestClient # type: ignore
from main import app
from db import db_notification

client = TestClient(app)

import unittest
class TestNotification(unittest.TestCase):
    
    def test_superadmin_get_notifications(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "username", "password": "password"}
        )
        access_token = login_response.json()["data"]["access_token"]
    
        response = client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_admin_get_notifications(self):
        login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        access_token = login_response.json()["data"]["access_token"]
    
        response = client.get(
        "/api/notifications",
        headers={"Authorization": f"Bearer {access_token}"}
    )
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_staff_get_notifications(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "staff_perusahaan", "password": "password"}
        )
        print(login_response)
        access_token = login_response.json()["data"]["access_token"]
    
        response = client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_reviewer_internal_get_notifications(self):
        login_response = client.post(
        "/api/auth",
        data={"username": "emma_jones", "password": "password"}
    )
        access_token = login_response.json()["data"]["access_token"]
    
        response = client.get(
        "/api/notifications",
        headers={"Authorization": f"Bearer {access_token}"}
    )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_reviewer_external_get_notifications(self):
        login_response = client.post(
        "/api/auth",
        data={"username": "reviewer", "password": "reviewer"}
    )
        access_token = login_response.json()["data"]["access_token"]
    
        response = client.get(
        "/api/notifications",
        headers={"Authorization": f"Bearer {access_token}"}
    )
        assert response.status_code == 200
        assert response.json()["success"] is True
        
if __name__ == "__main__":
    unittest.main()