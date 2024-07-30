import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app

from html_reporter import HTMLTestRunner
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import get_proof_by_filename, delete_proof_by_key, delete_assessment


client = TestClient(app)

import unittest
class TestAssessmentFDP(unittest.TestCase):

    @pytest.mark.order(1)
    def test_admin_start_asessment_success(self):
        # Pastikan last assessment harus sudah finish
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/api/assessment",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        # print(response.status_code)
        # print(response.json())

        
        assert response.status_code == 201
        assert response.json()["message"] == "Start assessment success"
        assert response.json()["success"] is True

    @pytest.mark.order(2)
    def test_admin_start_asessment_failed(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/api/assessment",
            headers={"Authorization": f"Bearer {access_token}"},
            json={}
        )
        # print(response.status_code)
        # print(response.json())
        
        assert response.status_code == 400
        assert response.json()["message"] == "Please finish last assessment first"
        assert response.json()["success"] is False

    @pytest.mark.order(3)
    def test_admin_update_assesment_point_not_found(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.patch(
            "/api/point",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "bab": 10,
                "sub_bab": 5.0,
                "point": 2,
                "answer": 3,
            })

        assert response.status_code == 404
        assert response.json()["message"] == 'Point not found'
        assert response.json()["success"] is False

    @pytest.mark.order(4)
    def test_admin_update_assesment_success(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/assessments",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == 'Success fetch data'
        assert response.json()["success"] is True

    @pytest.mark.order(5)
    def test_admin_get_assesment_list(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/assessments",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # client.delete('/api/dev/assessments')

        assert response.status_code == 200
        assert response.json()["message"] == 'Success fetch data'
        assert response.json()["success"] is True

    # def test_admin_get_detail_grade_from_reviewer(self):
    #     login_response = client.post(
    #         "/api/auth",
    #         data={"username": "adminperusahaan", "password": "admin"}
    #     )
    #     assert login_response.status_code == 200
    #     access_token = login_response.json()["data"]["access_token"]

    #     assessment_id = 'ev9ag3o7lxed'
    #     response = client.get(
    #         f"/api/assessment/insight{assessment_id}",
    #         headers={"Authorization": f"Bearer {access_token}"}
    #     )
        
    #     print(response.status_code)
    #     print(response.json())

    #     assert response.status_code == 200
    #     assert response.json()["message"] == 'Fetch data success'
    #     assert response.json()["success"] is True

    # def test_admin_get_detail_grade_from_reviewer_but_assignment_not_found(self):
    #     login_response = client.post(
    #         "/api/auth",
    #         data={"username": "adminperusahaan", "password": "admin"}
    #     )
    #     assert login_response.status_code == 200
    #     access_token = login_response.json()["data"]["access_token"]

    #     assessment_id = 'notfound'
    #     response = client.get(
    #         f"/api/assessment/insight/{assessment_id}",
    #         headers={"Authorization": f"Bearer {access_token}"}
    #     )

    #     assert response.status_code == 404
    #     assert response.json()["message"] == 'Assessment not found'
    #     assert response.json()["success"] is False


if __name__ == "__main__":
    runner = HTMLTestRunner(
        report_filepath="my_report.html",
        title="Test Assessment Admin",
        description="Ini Test Assessment Admin",
        open_in_browser=True
    )

    # run the test
    unittest.main(testRunner=runner)
