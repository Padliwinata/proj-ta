import sys
import os

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json

from fastapi.testclient import TestClient # type: ignore
from main import app
from db import db_assessment

client = TestClient(app)
base_url = "https://sandboxtech.cloud"

import unittest

class TestFraudDetection(unittest.TestCase):
    def test_get_report_unauthorized(self):
            response = client.get(
                f"/api/report",
            )

            assert response.status_code == 401
            assert response.json()["message"] == 'Unauthorized'
            assert response.json()["success"] is False

    def test_get_report_forbidden_access(self):
            login_response = client.post(
                "/api/auth",
                data={"username": "emma_jones", "password": "password"}
            )
            assert login_response.status_code == 200
            access_token = login_response.json()["data"]["access_token"]

            response = client.get(
                "/api/report",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 403
            assert response.json()["message"] == 'Forbidden access'
            assert response.json()["success"] is False

    def test_get_report_success(self):
            login_response = client.post(
                "/api/auth",
                data={"username": "adminperusahaan", "password": "admin"}
            )
            assert login_response.status_code == 200
            access_token = login_response.json()["data"]["access_token"]

            response = client.get(
                "/api/report",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200
            assert response.json()["message"] == 'Fetch data success'
            assert response.json()["success"] is True

    def test_get_report_by_key_forbidden_access(self):
            login_response = client.post(
                "/api/auth",
                data={"username": "emma_jones", "password": "password"}
            )
            assert login_response.status_code == 200
            access_token = login_response.json()["data"]["access_token"]

            report_key =  "05z11euth4id"
            response = client.get(
                f"/api/report/{report_key}",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 403
            assert response.json()["message"] == 'Forbidden access'
            assert response.json()["success"] is False

    def test_get_report_by_key_success(self):
            login_response = client.post(
                "/api/auth",
                data={"username": "adminperusahaan", "password": "admin"}
            )
            assert login_response.status_code == 200
            access_token = login_response.json()["data"]["access_token"]

            report_key =  "05z11euth4id"
            response = client.get(
                f"/api/report/{report_key}",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200
            assert response.json()["message"] == 'Fetch data success'
            assert response.json()["success"] is True

    def test_insert_report_unprocessable_entity(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "emma_jones", "password": "password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/report",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 422
        assert response.json()["detail"] == [
            {
                "loc": ["body"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]

    def test_insert_report_forbidden_access(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "emma_jones", "password": "password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/report",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "account_receivables_1": 153909929,
                "account_receivables_2": 211364131,
                "cash_flow_operate_1": 292733763,
                "cash_flow_operate_2": 487884312,
                "cogs_1": 1637778233,
                "cogs_2": 2017661985,
                "current_assets_1": 955934379,
                "current_assets_2": 1192611390,
                "depreciation_1": 145556996,
                "depreciation_2": 199692257,
                "id_institution": "gc8uupscjs0e",
                "net_continuous_1": 48164343,
                "net_continuous_2": 159960247,
                "ppe_1": 1520837177,
                "ppe_2": 1520837177,
                "revenue_1": 2824529865,
                "revenue_2": 3698268848,
                "securities_1": 11703633,
                "securities_2": 14959054,
                "sgae_1": 978404721,
                "sgae_2": 1286510421,
                "tahun_1": 2012,
                "tahun_2": 2013,
                "total_asset_1": 2085215,
                "total_asset_2": 2582866504,
                "total_ltd_1": 602268672,
                "total_ltd_2": 2582866504
            }
        )

        assert response.status_code == 403
        assert response.json()["message"] == 'Forbidden access'
        assert response.json()["success"] is False

    def test_insert_report_success(self):
        login_response = client.post(
            "/api/auth",
            data={"username": "adminperusahaan", "password": "admin"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.post(
            "/report",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "account_receivables_1": 153909929,
                "account_receivables_2": 211364131,
                "cash_flow_operate_1": 292733763,
                "cash_flow_operate_2": 487884312,
                "cogs_1": 1637778233,
                "cogs_2": 2017661985,
                "current_assets_1": 955934379,
                "current_assets_2": 1192611390,
                "depreciation_1": 145556996,
                "depreciation_2": 199692257,
                "id_institution": "gc8uupscjs0e",
                "net_continuous_1": 48164343,
                "net_continuous_2": 159960247,
                "ppe_1": 1520837177,
                "ppe_2": 1520837177,
                "revenue_1": 2824529865,
                "revenue_2": 3698268848,
                "securities_1": 11703633,
                "securities_2": 14959054,
                "sgae_1": 978404721,
                "sgae_2": 1286510421,
                "tahun_1": 2012,
                "tahun_2": 2013,
                "total_asset_1": 2085215,
                "total_asset_2": 2582866504,
                "total_ltd_1": 602268672,
                "total_ltd_2": 2582866504
            }
        )

        assert response.status_code == 201
        assert response.json()["message"] == 'Success insert report'
        assert response.json()["success"] is True

if __name__ == "__main__":
    unittest.main()