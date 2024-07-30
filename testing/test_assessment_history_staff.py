import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient # type: ignore
from main import app
from html_reporter import HTMLTestRunner


client = TestClient(app)

import unittest
class TestAssessmentHistoryStaff(unittest.TestCase):
    
    @pytest.mark.order(1)
    def test_staff_get_assessment_history(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "staff_perusahaan", "password": "password"}
        )
        access_token = login_response.json()["data"]["access_token"]
        
        # Assuming the database has assessments data
        response = client.get(
            "/api/assessments",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Success fetch data"
        assert response.json()["success"] is True


if __name__ == "__main__":
    runner = HTMLTestRunner(
        report_filepath="my_report.html",
        title="Test History Assessment Staff",
        description="Ini Test History Assessment Staff",
        open_in_browser=True
    )

    # run the test
    unittest.main(testRunner=runner)