import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app
from html_reporter import HTMLTestRunner

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
            "full_name": "John Doeeeeeeeeeeeee",
            "role": "staff",
            "phone": "1234567895098099",
            "email": "john.doeeeeeee@example.com",
            "username": "johndoeeeeeee",
            "password": "securepassworddddddd"
            
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
            "full_name": "John Doeeeeeeeeeeeee",
            "role": "staff",
            "phone": "1234567895098099",
            "email": "john.doeeeeeee@example.com",
            "username": "johndoeeeeeee",
            "password": "securepassworddddddd"
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
                "full_name": "Reviewer Internal 20",
                "role": "reviewer",
                "phone": "12345678901980899",
                "email": "reviewer.internal.20@example.com",
                "username": "reviewer.internal.20",
                "password": "securepasswordddddd"
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
                "full_name": "Reviewer Internal 20",
                "role": "reviewer",
                "phone": "12345678901980899",
                "email": "reviewer.internal.20@example.com",
                "username": "reviewer.internal.20",
                "password": "securepasswordddddd"
        }
    )
        assert response.status_code == 400
        assert response.json()["success"] is False
        assert response.json()["message"] == "User Already Exist"
        
    def test_admin_get_staff_list(self): #FR-SUP-03
        login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        access_token = login_response.json()["data"]["access_token"]
    
        response = client.get(
        "/api/staff",
        headers={"Authorization": f"Bearer {access_token}"}
    )
        
        print(response.status_code)
        print(response.json())

        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
    def test_admin_get_reviewer_internal_list(self): #FR-SUP-03
        login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        access_token = login_response.json()["data"]["access_token"]
    
        response = client.get(
        "/api/staff",
        headers={"Authorization": f"Bearer {access_token}"}
    )
        
        print(response.status_code)
        print(response.json())

        
        assert response.status_code == 200
        assert response.json()["success"] is True
    

            
if __name__ == "__main__":
    runner = HTMLTestRunner(
        report_filepath="my_report.html",
        title="Test Main Page Admin",
        description="Ini test main page",
        open_in_browser=True
    )

    # run the test
    unittest.main(testRunner=runner)