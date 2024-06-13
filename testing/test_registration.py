import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json

from fastapi.testclient import TestClient # type: ignore
from main import app
from main import register


client = TestClient(app)

import unittest
class TestRegistration(unittest.TestCase):
    def test_admin_registration(self): #test registrasi line 155
        response = client.post(
        "/api/register",
        json={
            "username": "admintesting5",
            "email": "admin5@testing.com",
            "password": "passwordd",
            "full_name": "Admin Testing 5",
            "role": "admin",
            "phone": "0829918837744",
            "institution_name": "Admin Institutionn",
            "institution_address": "Jl. Pahlawann",
            "institution_phone": "0829938847755",
            "institution_email": "adminn@institution.com"
        }
    )

        assert response.status_code == 201
        assert response.json()["message"] == "User registered successfully"
        assert response.json()["success"] is True
        
 

    def test_admin_registration_account_exist(self):
        response = client.post(
        "/api/register",
        json={
            "username": "admintesting5",
            "email": "admin5@testing.com",
            "password": "passwordd",
            "full_name": "Admin Testing 5",
            "role": "admin",
            "phone": "0829918837744",
            "institution_name": "Admin Institutionn",
            "institution_address": "Jl. Pahlawann",
            "institution_phone": "0829938847755",
            "institution_email": "adminn@institution.com"
        }
    )
        
           # Print the response for debugging
        print(response.status_code)
        print(response.json())

        assert response.status_code == 400
        assert response.json()["message"] == "Username or email already "
        assert response.json()["success"] is False

if __name__ == "__main__":
    unittest.main()

