import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
# Login Admin Handler
def access_token_admin():
    login_response = client.post(
        "/api/auth",
        data={
            "username": "adminperusahaan",
            "password": "admin"
        }
    )
    assert login_response.status_code == 200
    assert login_response.json()["success"] is True
    token = login_response.json()["data"]["access_token"]
    return token

@pytest.fixture(scope="module")
# Login Reviewer Intenal Handler
def access_token_reviewer_internal():
    login_response = client.post(
        "/api/auth",
        data={
            "username": "emma_jones",
            "password": "password"
        }
    )
    assert login_response.status_code == 200
    assert login_response.json()["success"] is True
    token = login_response.json()["data"]["access_token"]
    return token

@pytest.mark.order(1)
def test_admin_login():
    login_response = client.post(
        "/api/auth",
        data={
            "username": "adminperusahaan",
            "password": "admin"
        }
    )
    assert login_response.status_code == 200
    assert login_response.json()["success"] is True
    assert "access_token" in login_response.json()["data"]

@pytest.mark.order(2)
def test_get_fraud_assessments_history(access_token_admin):
    response = client.get(
        "/api/assessments",
        headers={"Authorization": f"Bearer {access_token_admin}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Success fetch data"
    assert response.json()["success"] is True

@pytest.mark.order(3)
def test_get_assessment_active(access_token_admin):
    response = client.get(
        "/api/assessment",
        headers={"Authorization": f"Bearer {access_token_admin}"},
        params={
            "sub_bab": "2.1"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Fetch data success"
    assert response.json()["success"] is True

@pytest.mark.order(4)
def test_get_assessment_active_not_found(access_token_admin):
    response = client.get(
        "/api/assessment",
        headers={"Authorization": f"Bearer {access_token_admin}"},
        params={
            "sub_bab": "3.3"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Empty data"
    assert response.json()["success"] is True

@pytest.mark.order(5)
def test_fill_assessment_point_already_exist(access_token_admin):
    response = client.post(
        "/api/point",
        headers={"Authorization": f"Bearer {access_token_admin}"},
        params={
            "bab": "3",
            "sub_bab": "3.2",
            "point": "1",
            "answer": "1"
        }
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Point already exist"
    assert response.json()["success"] is False

@pytest.mark.order(6)
def test_fill_assessment_invalid_sub_bab(access_token_admin):
    response = client.post(
        "/api/point",
        headers={"Authorization": f"Bearer {access_token_admin}"},
        params={
            "bab": "3",
            "sub_bab": "3.3",
            "point": "1",
            "answer": "1"
        }
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid sub bab"
    assert response.json()["success"] is False

@pytest.mark.order(7)
def test_fill_assessment_success(access_token_admin):
    response = client.post(
        "/api/point",
        headers={"Authorization": f"Bearer {access_token_admin}"},
        params={
            "bab": "1",
            "sub_bab": "1.2",
            "point": "1",
            "answer": "1"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.order(8)
def test_update_assessment(access_token_admin):
    response = client.patch(
        "/api/point",
        headers={"Authorization": f"Bearer {access_token_admin}"},
        params={
            "bab": "2",
            "sub_bab": "2.1",
            "point": "1",
            "answer": "1"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Update success"
    assert response.json()["success"] is True

@pytest.mark.order(9)
def test_submit_assessment(access_token_admin):
    response = client.post(
        "/api/selesai",
        headers={"Authorization": f"Bearer {access_token_admin}"},
        params={
            "id_assessment": "0j9ven13mzyr"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Assessment finished"
    assert response.json()["success"] is True

@pytest.mark.order(10)
def test_reviewer_internal_login():
    login_response = client.post(
        "/api/auth",
        data={
            "username": "emma_jones",
            "password": "password"
        }
    )
    assert login_response.status_code == 200
    assert login_response.json()["success"] is True
    assert "access_token" in login_response.json()["data"]

@pytest.mark.order(11)
def test_get_fraud_assessments_history_from_reviewer_internal(access_token_reviewer_internal):
    response = client.get(
        "/api/assessments",
        headers={"Authorization": f"Bearer {access_token_reviewer_internal}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Success fetch data"
    assert response.json()["success"] is True

    # Pengecekan untuk id_reviewer_internal kosong dan is_done = true
    assessments = response.json()["data"]
    filtered_assessments = [
        assessment for assessment in assessments
        if assessment["id_reviewer_internal"] == "" and assessment["is_done"]
    ]
    
    assert len(filtered_assessments) > 0, "No assessments with id_reviewer_internal empty and is_done = true found"

@pytest.mark.order(12)
def test_assessment_evaluation_failed(access_token_reviewer_internal):
    response = client.get(
        "/api/assessments/evaluation",
        headers={"Authorization": f"Bearer {access_token_reviewer_internal}"},
        params={
            "id_assessment": "0j9ven13mzyr"
        }
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Already reviewed by another internal reviewer"
    assert response.json()["success"] is False

@pytest.mark.order(13)
def test_assessment_evaluation_success(access_token_reviewer_internal):
    # ID Assessment ganti dengan id yang baru jika failed
    response = client.get(
        "/api/assessments/evaluation",
        headers={"Authorization": f"Bearer {access_token_reviewer_internal}"},
        params={
            "id_assessment": "9oqq3dwem8k1"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Start reviewing success"
    assert response.json()["success"] is True

@pytest.mark.order(14)
def test_do_assessment_evaluation(access_token_reviewer_internal):
    id_assessment = "4turk48okmdn"
    response = client.post(
        f"/api/assessments/evaluation",
        headers={"Authorization": f"Bearer {access_token_reviewer_internal}"},
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

@pytest.mark.order(15)
def test_submit_assessment_evaluation(access_token_reviewer_internal):
    response = client.get(
        "/api/assessments/finish",
        headers={"Authorization": f"Bearer {access_token_reviewer_internal}"},
        params={
            "id_assessment": "4rt70j4v2swm"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Reviewer finished"
    assert response.json()["success"] is True

@pytest.mark.order(16)
def test_get_fraud_assessments_history_from_reviewer_internal_after_submit(access_token_reviewer_internal):
    response = client.get(
        "/api/assessments",
        headers={"Authorization": f"Bearer {access_token_reviewer_internal}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Success fetch data"
    assert response.json()["success"] is True