import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

import unittest
class TestMainPageAdmin(unittest.TestCase):
    
    def test_upload_proof_point_success(self):
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
                    "bab": 5,
                    "sub_bab": 5.9,
                    "point": 5,
                    "answer": 3,
                }
            )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_upload_proof_point_forbidden_access(self):
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

    def test_upload_proof_point_file_too_large(self):
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

    def test_upload_proof_point_point_already_exist(self):
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
                    "bab": 5,
                    "sub_bab": 5.9,
                    "point": 5,
                    "answer": 3,
                }
            )
        assert response.status_code == 400
        assert response.json()["message"] == "Point already exist"
        assert response.json()["success"] is False

        
if __name__ == "__main__":
    unittest.main()