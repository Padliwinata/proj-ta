import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

def test_admin_get_login_history_empty_data():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    access_token = login_response.json()["data"]["access_token"]
    
    response = client.get(
        "/api/log",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Empty Data"
    assert response.json()["success"] is True

def test_admin_get_login_history():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    access_token = login_response.json()["data"]["access_token"]
    
    response = client.get(
        "/api/log",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Fetch Data Success"
    assert response.json()["success"] is True
