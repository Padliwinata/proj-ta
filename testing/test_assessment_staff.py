import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json

from fastapi.testclient import TestClient # type: ignore
from main import app
from db import db_assessment

client = TestClient(app)

import unittest
class TestAssessmentFDP(unittest.TestCase):

    def test_staff_update_assesment_success(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "bob_marley", "password": "yet_another_secure_password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.patch(
            "/api/point",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "bab": 1,
                "sub_bab": 1.1,
                "point": 1,
                "answer": 2,
            })

        assert response.status_code == 200
        assert response.json()["message"] == 'Update success'
        assert response.json()["success"] is True

    def test_staff_get_assesment_list(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "bob_marley", "password": "yet_another_secure_password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            f"/api/assessment",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == 'Success fetch data'
        assert response.json()["success"] is True

    def test_staff_get_detail_grade(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "bob_marley", "password": "yet_another_secure_password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        assessment_id = '36iczsgb8aux'
        response = client.get(
            f"/api/assessment/insight/{assessment_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == 'Fetch data success'
        assert response.json()["success"] is True
        
if __name__ == "__main__":
    unittest.main()

