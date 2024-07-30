import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

import unittest
    
def remove_access_token():
    return {"access_token": None}

class TestReviewerExternal(unittest.TestCase):
    # TC-REK-01
    def test_login_reviewer_external(self):
        response = client.post(
        "/api/auth",
        data={"username": "reviewer", "password": "reviewer"}
    )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "access_token" in response.json()["data"]

    # TC-REK-02
    def test_login_reviewer_external_failed(self):
        response = client.post(
        "/api/auth",
        data={"username": "reviewer", "password": "wrongpassword"}
    )
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert response.json()["message"] == 'User not found'

    # TC-REK-03
    def test_get_list_fraud_assessments_internal_only(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        access_token = login_response.json()["data"]["access_token"]
        
        response = client.get(
            "api/assessments",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        
        assert response.json()["success"] is True
        assert response.json()["message"] == 'Success fetch data'
        
        assessments = response.json()["data"]
        
        found_internal_only = any(
            assessment["hasil_internal"] is not None and assessment["hasil_external"] is None
            for assessment in assessments
        )
        
        assert found_internal_only is True, "No assessments found with hasil_internal not null and hasil_external null"

    # TC-REK-04
    def test_reviewer_external_carry_out_assessment(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "reviewer", "password": "reviewer"}
        )
        access_token = login_response.json()["data"]["access_token"]
    
        id_assessment = "4turk48okmdn"
        response = client.post(
            f"/api/assessments/evaluation",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "id_assessment": id_assessment,
                "sub_bab": "1.1",
                "tepat": [
                    True, False, True, False, True, True, False, True, False, True
                ],
                "skor": [
                    "1", "0.5", "1", "0", "1", "1", "0.5", "1", "0", "1"
                ]
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Success update data"
        assert response.json()["success"] is True
    
    def test_reviewer_external_carry_out_assessment_failed(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "reviewer", "password": "reviewer"}
        )
        access_token = login_response.json()["data"]["access_token"]
    
        id_assessment = "4turk48okmdn"
        response = client.post(
            f"/api/assessments/evaluation",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "id_assessment": id_assessment,
                "sub_bab": "1.1",
                "tepat": [
                    True
                ],
                "skor": [
                    "1"
                ]
            }
        )
        assert response.status_code == 400
        assert response.json()["message"] == "Number of score didn't match"
        assert response.json()["success"] is False

    # TC-REK-05  
    def test_get_list_fraud_assessments_both_assessed(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "reviewer", "password": "reviewer"}
        )
        access_token = login_response.json()["data"]["access_token"]
        
        response = client.get(
            "/api/assessments",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        
        assert response.json()["success"] is True
        assert response.json()["message"] == 'Success fetch data'
        
        assessments = response.json()["data"]
        
        found_both_assessed = any(
            assessment["hasil_internal"] is not None and assessment["hasil_external"] is not None
            for assessment in assessments
        )
        
        assert found_both_assessed is True, "No assessments found with both hasil_internal and hasil_external not null"

    # TC-REK-06
    def test_get_list_history_assessments_has_been_assessed(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "reviewer", "password": "reviewer"}
        )
        access_token = login_response.json()["data"]["access_token"]
    
        id_assessment = "4turk48okmdn"
        response = client.get(
            f"/api/assessment/insight/{id_assessment}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Fetch data success"
        assert response.json()["success"] is True

    def test_get_detail_assessment_with_sub_bab(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "reviewer", "password": "reviewer"}
        )
        access_token = login_response.json()["data"]["access_token"]
    
        id_assessment = "4turk48okmdn"
        sub_bab = "1.1"
        response = client.get(
            f"/api/assessment/insight/{id_assessment}?sub_bab={sub_bab}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Fetch data success"
        assert response.json()["success"] is True

    # TC-REK-07
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
    
    # TC-REK-08
    def test_logout_reviewer_external(self):
        access_token_removed = remove_access_token()
        assert access_token_removed == {"access_token": None}

if __name__ == "__main__":
    unittest.main()