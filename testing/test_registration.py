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
                "username": "admintesting13",
                "email": "admin13@testing.com",
                "password": "password",
                "full_name": "Admin Testing 13",
                "role": "admin",
                "phone": "123456789",
                "institution_name": "Admin Institutiooon",
                "institution_address": "Jl. Pahlawann",
                "institution_phone": "987654321",
                "institution_email": "admin13@institution.com"
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
                "username": "admintesting13",
                "email": "admin13@testing.com",
                "password": "password",
                "full_name": "Admin Testing 13",
                "role": "admin",
                "phone": "123456789",
                "institution_name": "Admin Institutiooon",
                "institution_address": "Jl. Pahlawann",
                "institution_phone": "987654321",
                "institution_email": "admin13@institution.com"
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