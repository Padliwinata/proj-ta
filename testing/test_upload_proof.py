import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient  # type: ignore
from main import app
from db import delete_proof_by_key, get_proof_by_filename
from html_reporter import HTMLTestRunner
import pytest

client = TestClient(app)

import unittest
class TestUploadProof(unittest.TestCase):
    
    @pytest.mark.order(1)
    def test_upload_proof_point_success(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        # Buka file untuk mengunggahnya
        if os.getcwd() == '/Users/rpadliwinata/PycharmProjects/devta/proj-ta/testing':
            file_path = "test_files/lampiran.pdf"
        else:
            file_path = "testing/test_files/lampiran.pdf"
        with open(file_path, "rb") as file:
            response = client.post(
                "/api/point",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": ("lampiran.pdf", file, "application/pdf")},
                params={
                    "bab": "5",
                    "sub_bab": "5.1",
                    "point": 2,
                    "answer": 1,
                }
            )

        # data = get_proof_by_filename('gc8uupscjs0e_5_52_5.0.pdf')
        # delete_proof_by_key(data['data_key'])

        assert response.status_code == 200
        assert response.json()["success"] is True
    
    @pytest.mark.order(2)
    def test_upload_proof_point_invalid_bab(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        file_path = "testing/test_files/lampiran.pdf"
        with open(file_path, "rb") as file:
            response = client.post(
                "/api/point",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": ("lampiran.pdf", file, "application/pdf")},
                params={
                    "bab": "10",
                    "sub_bab": "2.2",
                    "point": 2,
                    "answer": 1,
                }
            )

        assert response.status_code == 400
        assert response.json()["message"] == "Invalid bab"
        assert response.json()["success"] is False
        
    @pytest.mark.order(3)
    def test_upload_proof_point_invalid_sub_bab(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        file_path = "testing/test_files/lampiran.pdf"
        with open(file_path, "rb") as file:
            response = client.post(
                "/api/point",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": ("lampiran.pdf", file, "application/pdf")},
                params={
                    "bab": "5",
                    "sub_bab": "5.5",
                    "point": 2,
                    "answer": 1,
                }
            )

        assert response.status_code == 400
        assert response.json()["message"] == "Invalid sub bab"
        assert response.json()["success"] is False

    @pytest.mark.order(4)
    def test_upload_proof_point_already_exist(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        # Assume point already exists
        if os.getcwd() == '/Users/rpadliwinata/PycharmProjects/devta/proj-ta/testing':
            file_path = "test_files/lampiran.pdf"
        else:
            file_path = "testing/test_files/lampiran.pdf"
        with open(file_path, "rb") as file:
            client.post(
                "/api/point",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": ("lampiran.pdf", file, "application/pdf")},
                params={
                    "bab": "5",
                    "sub_bab": "5.1",
                    "point": 2,
                    "answer": 1,
                }
            )

            response = client.post(
                "/api/point",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": ("lampiran.pdf", file, "application/pdf")},
                params={
                    "bab": "5",
                    "sub_bab": "5.1",
                    "point": 2,
                    "answer": 1,
                }
            )
        # data = get_proof_by_filename('gc8uupscjs0e_5_51_5.0.pdf')
        # delete_proof_by_key(data['data_key'])

        assert response.status_code == 400
        assert response.json()["message"] == "Point already exist"
        assert response.json()["success"] is False

    @pytest.mark.order(4)
    def test_upload_proof_point_forbidden_access(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "username", "password": "password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        # Buka file untuk mengunggahnya
        if os.getcwd() == '/Users/rpadliwinata/PycharmProjects/devta/proj-ta/testing':
            file_path = "test_files/lampiran.pdf"
        else:
            file_path = "testing/test_files/lampiran.pdf"
        with open(file_path, "rb") as file:
            response = client.post(
                "/api/point",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": ("lampiran.pdf", file, "application/pdf")},
                params={
                    "bab": "4",
                    "sub_bab": "4.2",
                    "point": 2,
                    "answer": 3,
                }
            )

        assert response.status_code == 403
        assert response.json()["success"] is False
        
    @pytest.mark.order(5)
    def test_upload_proof_point_file_too_large(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

    # Buka file untuk mengunggahnya
        if os.getcwd() == '/Users/rpadliwinata/PycharmProjects/devta/proj-ta/testing':
            file_path = "test_files/lampiran.pdf"
        else:
            file_path = "testing/test_files/lampiran.pdf"
        with open(file_path, "rb") as file:
            response = client.post(
                "/api/point",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": ("largefile.pdf", file, "application/pdf")},
                params={
                    "bab": "4",
                    "sub_bab": "4.1",
                    "point": 2,
                    "answer": 3,
                }
            )

        # data = get_proof_by_filename('gc8uupscjs0e_4_41_2.0.pdf')
        # delete_proof_by_key(data['data_key'])

        assert response.status_code == 413
        assert response.json()["message"] == "File Too Large"
        assert response.json()["success"] is False
        
if __name__ == "__main__":
    runner = HTMLTestRunner(
        report_filepath="my_report.html",
        title="Test Upload Proof",
        description="Ini Test Upload Proof",
        open_in_browser=True
    )

    # run the test
    unittest.main(testRunner=runner)
