import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app
from html_reporter import HTMLTestRunner

client = TestClient(app)

import unittest
class TestGetStaffList(unittest.TestCase):
    def test_admin_get_staff_list(self): #FR-SUP-03
        login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        access_token = login_response.json()["data"]["access_token"]
    
        response = client.get(
        "/api/staff",
        headers={"Authorization": f"Bearer {access_token}"}
    )
        
        print(response.status_code)
        print(response.json())

        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
    def test_admin_get_reviewer_internal_list(self): #FR-SUP-03
        login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
        access_token = login_response.json()["data"]["access_token"]
    
        response = client.get(
        "/api/staff",
        headers={"Authorization": f"Bearer {access_token}"}
    )
        
        print(response.status_code)
        print(response.json())

        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
if __name__ == "__main__":
    runner = HTMLTestRunner(
        report_filepath="my_report.html",
        title="Test Admin Get Staff List",
        description="Ini Test Admin Get Staff List",
        open_in_browser=True
    )

    # run the test
    unittest.main(testRunner=runner)