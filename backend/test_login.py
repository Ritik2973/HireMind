from fastapi.testclient import TestClient
from main import app
from sqlalchemy import select
from database.connection import SessionLocal
from models.user import User
from security.jwt import verify_token

client = TestClient(app)

def setup_test_user():
    db = SessionLocal()
    # Delete if exists
    db.execute(User.__table__.delete().where(User.email == "logintest@example.com"))
    db.commit()
    
    # Register a clean user
    payload = {
        "name": "Login Test User",
        "email": "logintest@example.com",
        "password": "strongpassword123",
        "target_job_role": "Backend Engineer"
    }
    client.post("/auth/register", json=payload)
    db.close()

def run_tests():
    print("--- Running tests ---")
    setup_test_user()

    # TEST 1: Login with valid credentials
    print("\nTEST 1: Valid user login")
    payload1 = {
        "email": "logintest@example.com",
        "password": "strongpassword123"
    }
    response1 = client.post("/auth/login", json=payload1)
    print("Status:", response1.status_code)
    resp_json = response1.json()
    assert response1.status_code == 200
    assert "access_token" in resp_json
    assert "password" not in resp_json
    assert "password_hash" not in resp_json
    print("Successfully retrieved access token.")
    token = resp_json["access_token"]

    # TEST 2: Incorrect password
    print("\nTEST 2: Incorrect password")
    payload2 = {
        "email": "logintest@example.com",
        "password": "wrongpassword"
    }
    response2 = client.post("/auth/login", json=payload2)
    print("Status:", response2.status_code)
    print("Response detail:", response2.json().get("detail"))
    assert response2.status_code == 401
    assert response2.json().get("detail") == "Incorrect email or password"

    # TEST 3: Email does not exist
    print("\nTEST 3: Email does not exist")
    payload3 = {
        "email": "doesnotexist@example.com",
        "password": "strongpassword123"
    }
    response3 = client.post("/auth/login", json=payload3)
    print("Status:", response3.status_code)
    print("Response detail:", response3.json().get("detail"))
    assert response3.status_code == 401
    assert response3.json().get("detail") == "Incorrect email or password"

    # TEST 4: Verify response does not contain password/password_hash (done in TEST 1)
    print("\nTEST 4: Verified response does not contain password/password_hash in TEST 1")

    # TEST 5: Verify JWT
    print("\nTEST 5: Verify JWT")
    payload = verify_token(token)
    assert payload is not None
    assert "sub" in payload
    print("JWT Subject (User ID):", payload["sub"])
    assert "password" not in payload
    assert "password_hash" not in payload
    print("JWT successfully validated and does not contain sensitive data.")

    print("\nAll login tests passed successfully!")

if __name__ == "__main__":
    run_tests()
