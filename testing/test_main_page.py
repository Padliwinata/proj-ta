import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient # type: ignore
from main import app

client = TestClient(app)

def test_superadmin_get_admin_list():
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

def test_superadmin_activate_admin():
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

def test_superadmin_deactivate_admin():
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

def test_superadmin_get_notifications():
    login_response = client.post(
        "/api/auth",
        data={"username": "username", "password": "password"}
    )
    access_token = login_response.json()["data"]["access_token"]
    
    response = client.get(
        "/api/notifications",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_admin_add_staff_account():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "John Doee",
            "role": "staff",
            "phone": "1234567890",
            "email": "john.doee@example.com",
            "username": "johndoee",
            "password": "securepasswordd"
        }
    )
    assert response.status_code == 201
    assert response.json()["success"] is True

def test_admin_add_staff_account_exists():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "John Doee",
            "role": "staff",
            "phone": "1234567890",
            "email": "john.doee@example.com",
            "username": "johndoee",
            "password": "securepasswordd"
        }
    )
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "User Already Exist"

def test_admin_add_reviewer_internal_account():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "Reviewer Internal 3",
            "role": "reviewer",
            "phone": "12345678901",
            "email": "reviewer.internal.3@example.com",
            "username": "reviewer.internal.3",
            "password": "securepasswordd"
        }
    )
    assert response.status_code == 201
    assert response.json()["success"] is True

def test_admin_add_reviewer_internal_account_exist():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "Reviewer Internal 3",
            "role": "reviewer",
            "phone": "12345678901",
            "email": "reviewer.internal.3@example.com",
            "username": "reviewer.internal.3",
            "password": "securepasswordd"
        }
    )
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "User Already Exist"

# Belum ada di sheet (-)

def test_admin_add_staff_missing_full_name():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "role": "staff",
            "phone": "081234567890",
            "email": "staff@example.com",
            "username": "staffuser",
            "password": "password123"
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["loc"] == ["body", "full_name"]

def test_admin_add_staff_missing_role():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "Staff Name",
            "phone": "081234567890",
            "email": "staff@example.com",
            "username": "staffuser",
            "password": "password123"
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["loc"] == ["body", "role"]

def test_admin_add_staff_missing_phone():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "Staff Name",
            "role": "staff",
            "email": "staff@example.com",
            "username": "staffuser",
            "password": "password123"
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["loc"] == ["body", "phone"]

def test_admin_add_staff_missing_email():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "Staff Name",
            "role": "staff",
            "phone": "081234567890",
            "username": "staffuser",
            "password": "password123"
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["loc"] == ["body", "email"]

def test_admin_add_staff_missing_username():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "Staff Name",
            "role": "staff",
            "phone": "081234567890",
            "email": "staff@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["loc"] == ["body", "username"]

def test_admin_add_staff_missing_password():
    login_response = client.post(
        "/api/auth",
        data={"username": "adminperusahaan", "password": "admin"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/api/account",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "Staff Name",
            "role": "staff",
            "phone": "081234567890",
            "email": "staff@example.com",
            "username": "staffuser"
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["loc"] == ["body", "password"]

def test_admin_activate_staff():
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

    # Cari data staff dengan role === 'staff'
    user_data = next((user for user in response.json()["data"] if user["role"] == "staff"), None)

    print(user_data)  # Print the user_data to see the details of the staff user

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
            print("The staff is already active, no action taken.")
    else:
        print("No staff user found.")


def test_admin_deactivate_staff():
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

    # Cari data staff dengan role === 'staff'
    user_data = next((user for user in response.json()["data"] if user["role"] == "staff"), None)

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
            print("The staff is already deactivated, no action taken.")
    else:
        print("No staff user found.")

def test_admin_activate_reviewer():
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

def test_admin_deactivate_reviewer():
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
