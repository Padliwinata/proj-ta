import sys
import os
import unittest
from fastapi.testclient import TestClient
from main import app
from html_reporter import HTMLTestRunner
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


client = TestClient(app)


class TestAssessmentFDP(unittest.TestCase):
    
    def test_admin_unfinished_asessment(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/api/selesai",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "id_assessment": "n7v8yzxyhypz"
            }
        )
        
        assert response.status_code == 400
        assert response.json()["message"] == "Unfinished assessment"
        assert response.json()["success"] is False

    def test_admin_finish_asessment(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/api/selesai",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "id_assessment": "05p9ut2hmkx4"
            }
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Assessment finished"
        assert response.json()["success"] is True

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
        
        assert response.status_code == 400
        assert response.json()["message"] == "Please finish last assessment first"
        assert response.json()["success"] is False

    def test_admin_start_asessment_success(self):
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

        assert response.status_code == 201
        assert response.json()["message"] == "Start assessment success"
        assert response.json()["success"] is True
    
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
                "sub_bab": 5.1,
                "point": 2,
                "answer": 3,
            })

        assert response.status_code == 404
        assert response.json()["message"] == 'Point not found'
        assert response.json()["success"] is False

    def test_admin_update_assesment_point_success(self):
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
                "bab": 11,
                "sub_bab": 1.0,
                "point": 1,
                "answer": 2,
            })

        assert response.status_code == 200
        assert response.json()["message"] == 'Update success'
        assert response.json()["success"] is True

    def test_admin_update_assesment_success(self):
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
                "bab": 11,
                "sub_bab": 1.0,
                "point": 1,
                "answer": 2,
            })

        assert response.status_code == 200
        assert response.json()["message"] == 'Update success'
        assert response.json()["success"] is True

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

        assert response.status_code == 200
        assert response.json()["message"] == 'Success fetch data'
        assert response.json()["success"] is True

    def test_admin_get_detail_grade_from_reviewer(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        assessment_id = '05p9ut2hmkx4'
        response = client.get(
            f"/api/assessment/insight/{assessment_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == 'Fetch data success'
        assert response.json()["success"] is True

    def test_admin_get_detail_grade_from_reviewer_but_assignment_not_found(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        assessment_id = 'notfound'
        response = client.get(
            f"/api/assessment/insight/{assessment_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 404
        assert response.json()["message"] == 'Assessment not found'
        assert response.json()["success"] is False


if __name__ == "__main__":
    runner = HTMLTestRunner(
        report_filepath="my_report.html",
        title="Test Assessment",
        description="Ini test login",
        open_in_browser=True
    )

    # run the test
    unittest.main(testRunner=runner)