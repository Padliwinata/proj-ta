import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import pytest

from fastapi.testclient import TestClient # type: ignore
from main import app
from html_reporter import HTMLTestRunner

from db import db_assessment

client = TestClient(app)

import unittest
class TestPenilaianAssessment(unittest.TestCase):
    
    @pytest.mark.order(1)
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
                "id_assessment": "iv8xqg940eo5" #harus diganti dengan id assessment yang belum dinilai
            })

        assert response.status_code == 200
        assert response.json()["message"] == 'Start reviewing success'
        assert response.json()["success"] is True
    
    @pytest.mark.order(2)
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
                "id_assessment": "iv8xqg940eo5" 
            })

        assert response.status_code == 400
        assert response.json()["message"] == 'Already reviewed by another internal reviewer'
        assert response.json()["success"] is False
        
    @pytest.mark.order(3)
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
        assert response.json()["message"] == 'Empty data'
        assert response.json()["success"] is True
        
    @pytest.mark.order(4)
    def test_reviewer_internal_get_assesment_list_empty_data(self):
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
        assert response.json()["message"] == 'Empty data'
        assert response.json()["success"] is True
        
if __name__ == "__main__":
    runner = HTMLTestRunner(
        report_filepath="my_report.html",
        title="Test Penilaian Reviewer Internal",
        description="Test Penilaian Assessment oleh Reviewer Internal",
        open_in_browser=True
    )

    # run the test
    unittest.main(testRunner=runner)