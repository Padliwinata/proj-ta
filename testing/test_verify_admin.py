import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app
from html_reporter import HTMLTestRunner

client = TestClient(app)

import unittest
class TestVerifyAdmin(unittest.TestCase):
    
    def test_superadmin_activate_admin(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "username", "password": "password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/admin",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        user_data = response.json()["data"][0]
        user_id = user_data["id"]
        is_active = user_data["is_active"]

        if not is_active:
            toggle_response = client.get(
                f"/api/verify/{user_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            assert toggle_response.status_code == 200

            response = client.get(
                "/api/admin",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == 200
            assert response.json()["success"] is True

            updated_user_data = next(user for user in response.json()["data"] if user["id"] == user_id)

            assert updated_user_data["is_active"] == (not is_active)
        else:
            print("The user is already active, no action taken.")
            
    def test_superadmin_deactivate_admin(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "username", "password": "password"}
        )
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/admin",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        user_data = response.json()["data"][0]
        user_id = user_data["id"]
        is_active = user_data["is_active"]

        if is_active:
            toggle_response = client.get(
                f"/api/verify/{user_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert toggle_response.status_code == 200

            response = client.get(
                "/api/admin",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200
            assert response.json()["success"] is True

            updated_user_data = next(user for user in response.json()["data"] if user["id"] == user_id)
        
            assert updated_user_data["is_active"] == (not is_active)
        else:
            print("The user is already inactive, no action taken.")

if __name__ == "__main__":
    runner = HTMLTestRunner(
        report_filepath="my_report.html",
        title="Test Verify Admin",
        description="Test Verify Admin oleh Superadmin",
        open_in_browser=True
    )

    # run the test
    unittest.main(testRunner=runner)
