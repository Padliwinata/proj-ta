import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json

from fastapi.testclient import TestClient # type: ignore
from main import app
from main import register
from db import delete_user_by_username
from html_reporter import HTMLTestRunner


client = TestClient(app)

import unittest
class TestRegistration(unittest.TestCase):
    def test_admin_registration(self): #test registrasi line 155
        response = client.post(
            "/api/register",
            json={
                "username": "admintesting10",
                "email": "admin10@testing.com",
                "password": "passworddddd",
                "full_name": "Admin Testing 10",
                "role": "admin",
                "phone": "082991883774430",
                "institution_name": "Admin Institutionnnnn",
                "institution_address": "Jl. Pahlawann",
                "institution_phone": "082993884775530",
                "institution_email": "adminnnnn@institution.com"
            }
        )

        assert response.status_code == 201
        assert response.json()["message"] == "User registered successfully"
        assert response.json()["success"] is True

    def test_admin_registration_account_exist(self):
        username = "admintesting5"
        response = client.post(
        "/api/register",
        json={
                "username": "admintesting10",
                "email": "admin10@testing.com",
                "password": "passworddddd",
                "full_name": "Admin Testing 10",
                "role": "admin",
                "phone": "082991883774430",
                "institution_name": "Admin Institutionnnnn",
                "institution_address": "Jl. Pahlawann",
                "institution_phone": "082993884775530",
                "institution_email": "adminnnnn@institution.com"
        }
    )
        
           # Print the response for debugging
        print(response.status_code)
        print(response.json())

        assert response.status_code == 400
        assert response.json()["message"] == "Username or email already exist"
        assert response.json()["success"] is False

        delete_user_by_username(username)

if __name__ == "__main__":
    runner = HTMLTestRunner(
        report_filepath="my_report.html",
        title="Test Register Admin",
        description="Ini Test Register Admin",
        open_in_browser=True
    )

    # run the test
    unittest.main(testRunner=runner)