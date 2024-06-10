import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

def test_upload_proof_point_success():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    # Buka file untuk mengunggahnya
    file_path = "testing/test_files/lampiran.pdf"
    with open(file_path, "rb") as file:
        response = client.post(
            "/api/point",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": ("lampiran.pdf", file, "application/pdf")},
            params={
                "bab": 4,
                "sub_bab": 4.9,
                "point": 2,
                "answer": 3,
            }
        )

    assert response.status_code == 200
    assert response.json()["success"] is True

def test_upload_proof_point_forbidden_access():
    login_response = client.post(
        "/api/auth",
        data={"username": "username", "password": "password"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    # Buka file untuk mengunggahnya
    file_path = "testing/test_files/lampiran.pdf"
    with open(file_path, "rb") as file:
        response = client.post(
            "/api/point",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": ("lampiran.pdf", file, "application/pdf")},
            params={
                "bab": 4,
                "sub_bab": 4.10,
                "point": 2,
                "answer": 3,
            }
        )

    assert response.status_code == 403
    assert response.json()["success"] is False

def test_upload_proof_point_file_too_large():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

   # Buka file untuk mengunggahnya
    file_path = "testing/test_files/largefile.pdf"
    with open(file_path, "rb") as file:
        response = client.post(
            "/api/point",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": ("largefile.pdf", file, "application/pdf")},
            params={
                "bab": 4,
                "sub_bab": 4.11,
                "point": 2,
                "answer": 3,
            }
        )
    assert response.status_code == 413
    assert response.json()["message"] == "File Too Large"
    assert response.json()["success"] is False

def test_upload_proof_point_point_already_exist():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    # Assume point already exists
    file_path = "testing/test_files/lampiran.pdf"
    with open(file_path, "rb") as file:
        response = client.post(
            "/api/point",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": ("lampiran.pdf", file, "application/pdf")},
            params={
                "bab": 1,
                "sub_bab": 1.1,
                "point": 1,
                "answer": 3,
            }
        )
    assert response.status_code == 400
    assert response.json()["message"] == "Point already exist"
    assert response.json()["success"] is False

def test_admin_start_asessment_failed():
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

def test_admin_start_asessment_success():
    # Pastikan last assessment harus sudah finish
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

def test_admin_update_assesment_point_not_found():
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

def test_admin_update_assesment_success():
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

def test_admin_get_assesment_list():
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

def test_admin_get_detail_grade_from_reviewer_but_assignment_not_found():
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

def test_admin_get_detail_grade_from_reviewer():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
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

def test_staff_update_assesment_success():
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

def test_staff_get_assesment_list():
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

def test_staff_get_detail_grade():
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

