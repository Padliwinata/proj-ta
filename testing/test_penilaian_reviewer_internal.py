import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json

from fastapi.testclient import TestClient # type: ignore
from main import app
from db import db_assessment

client = TestClient(app)

import unittest
class TestPenilaianAssessment(unittest.TestCase):
    
    def test_reviewer_provide_assessment_already_reviewed(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "emma_jones", "password": "password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/assessments/evaluation",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "id_assessment": "05p9ut2hmkx4" 
            })

        assert response.status_code == 400
        assert response.json()["message"] == 'Already reviewed by another internal reviewer'
        assert response.json()["success"] is False

    def test_reviewer_provide_assessment_success(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "emma_jones", "password": "password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/assessments/evaluation",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "id_assessment": "8qmzna65io8j" #harus diganti dengan id assessment yang belum dinilai
            })

        assert response.status_code == 200
        assert response.json()["message"] == 'Start reviewing success'
        assert response.json()["success"] is True
        
    def test_reviewer_internal_get_assesment_list(self):
        login_response = client.post(
            "/api/auth",
           data={"username": "emma_jones", "password": "password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/assessments/list",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == 'Successfully fetch assessments'
        assert response.json()["success"] is True
        
if __name__ == "__main__":
    unittest.main()