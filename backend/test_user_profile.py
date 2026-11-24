from fastapi.testclient import TestClient
from main import app
from database.connection import SessionLocal
from models.user import User
import uuid

client = TestClient(app)

def setup_test_users():
    db = SessionLocal()
    # Clean up old test users to avoid collision
    db.execute(User.__table__.delete().where(User.email.in_(["profile_test@example.com", "other_user@example.com"])))
    db.commit()
    
    # Register main test user
    payload = {
        "name": "Profile Test User",
        "email": "profile_test@example.com",
        "password": "strongpassword123",
        "target_job_role": "Data Analyst"
    }
    client.post("/auth/register", json=payload)

    # Register a second user to test duplicate email collision
    payload2 = {
        "name": "Other User",
        "email": "other_user@example.com",
        "password": "strongpassword123",
        "target_job_role": "Backend Dev"
    }
    client.post("/auth/register", json=payload2)
    db.close()

def run_tests():
    print("--- Running tests for User Profile API ---")
    setup_test_users()

    # 1. Login to get token
    res_login = client.post("/auth/login", json={"email": "profile_test@example.com", "password": "strongpassword123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # TEST 1: GET profile with valid JWT
    print("\nTEST 1: GET profile with valid JWT")
    res1 = client.get("/users/me", headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    print("Response keys:", list(data1.keys()))
    assert data1["name"] == "Profile Test User"
    assert "password_hash" not in data1

    # TEST 2: GET profile without JWT
    print("\nTEST 2: GET profile without JWT")
    res2 = client.get("/users/me")
    assert res2.status_code == 401

    # TEST 3: UPDATE own profile with valid JWT
    print("\nTEST 3: UPDATE own profile with valid JWT")
    update_payload = {
        "name": "Updated Test User",
        "target_job_role": "Senior Data Analyst"
    }
    res3 = client.put("/users/me", headers=headers, json=update_payload)
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["name"] == "Updated Test User"
    assert data3["target_job_role"] == "Senior Data Analyst"

    # TEST 4: Invalid profile data (e.g. name too short)
    print("\nTEST 4: Invalid profile data")
    res4 = client.put("/users/me", headers=headers, json={"name": "A"})
    assert res4.status_code == 422

    # TEST 5: Update email to one that already exists
    print("\nTEST 5: Duplicate email test")
    res5 = client.put("/users/me", headers=headers, json={"email": "other_user@example.com"})
    assert res5.status_code == 409
    
    print("\nAll User Profile tests passed successfully!")

if __name__ == "__main__":
    run_tests()
