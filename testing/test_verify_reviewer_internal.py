import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

import unittest
class TestVerifyReviewerInternal(unittest.TestCase):
    
    def test_admin_activate_reviewer(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/staff",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Cari data staff dengan role === 'reviewer'
        user_data = next((user for user in response.json()["data"] if user["role"] == "reviewer"), None)

        if user_data:
            user_id = user_data["key"]
            is_active = user_data["status"]

            if not is_active:
                toggle_response = client.get(
                    f"/api/verify/{user_id}",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                assert toggle_response.status_code == 200

                response = client.get(
                    "/api/staff",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                assert response.status_code == 200
                assert response.json()["success"] is True

                updated_user_data = next(user for user in response.json()["data"] if user["key"] == user_id)

                assert updated_user_data["status"] == (not is_active)
            else:
                print("The reviewer is already active, no action taken.")
        else:
            print("No reviewer user found.")

    def test_admin_deactivate_reviewer(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/staff",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Cari data staff dengan role === 'reviewer'
        user_data = next((user for user in response.json()["data"] if user["role"] == "reviewer"), None)

        if user_data:
            user_id = user_data["key"]
            is_active = user_data["status"]

            if is_active:
                toggle_response = client.get(
                    f"/api/verify/{user_id}",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                assert toggle_response.status_code == 200

                response = client.get(
                    "/api/staff",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                assert response.status_code == 200
                assert response.json()["success"] is True

                updated_user_data = next(user for user in response.json()["data"] if user["key"] == user_id)

                assert updated_user_data["status"] is False  # Assert status is now False
            else:
                print("The reviewer is already deactivated, no action taken.")
        else:
            print("No reviewer user found.")
            
if __name__ == "__main__":
    unittest.main()