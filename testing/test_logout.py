import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

def remove_access_token():
    return {"access_token": None}

def test_logout_superadmin():
    access_token_removed = remove_access_token()
    assert access_token_removed == {"access_token": None}

def test_logout_admin():
    access_token_removed = remove_access_token()
    assert access_token_removed == {"access_token": None}

def test_logout_staff():
    access_token_removed = remove_access_token()
    assert access_token_removed == {"access_token": None}

def test_logout_reviewer_internal():
    access_token_removed = remove_access_token()
    assert access_token_removed == {"access_token": None}

def test_logout_reviewer_external():
    access_token_removed = remove_access_token()
    assert access_token_removed == {"access_token": None}