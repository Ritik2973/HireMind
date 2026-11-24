from fastapi.testclient import TestClient
from main import app
from sqlalchemy import select
from database.connection import SessionLocal
from models.user import User

client = TestClient(app)

def run_tests():
    print("--- Running tests ---")

    # Clean up DB for the test email
    db = SessionLocal()
    db.execute(User.__table__.delete().where(User.email == "test@example.com"))
    db.commit()

    # TEST 1: Valid new user registration
    print("\nTEST 1: Valid new user registration")
    payload1 = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "strongpassword123",
        "target_job_role": "Data Scientist"
    }
    response1 = client.post("/auth/register", json=payload1)
    print("Status:", response1.status_code)
    # Be careful not to log password hash
    resp_json = response1.json()
    print("Response Keys:", list(resp_json.keys()))
    assert response1.status_code == 201
    assert "password" not in resp_json
    assert "password_hash" not in resp_json

    # TEST 2: Same email again
    print("\nTEST 2: Same email again")
    response2 = client.post("/auth/register", json=payload1)
    print("Status:", response2.status_code)
    print("Response detail:", response2.json().get("detail"))
    assert response2.status_code == 409

    # TEST 3: Invalid/missing data
    print("\nTEST 3: Invalid/missing data")
    payload3 = {
        "name": "A", # Too short
        "email": "not-an-email",
        "password": "123" # Too short
    }
    response3 = client.post("/auth/register", json=payload3)
    print("Status:", response3.status_code)
    assert response3.status_code == 422

    # TEST 4: Verify DB contains hash
    print("\nTEST 4: Verify DB contains hash")
    db = SessionLocal()
    user = db.execute(select(User).where(User.email == "test@example.com")).scalar_one_or_none()
    assert user is not None
    print(f"User in DB: email={user.email}")
    print(f"Is password plain text? {'Yes' if user.password_hash == 'strongpassword123' else 'No'}")
    print(f"Is it Argon2? {'Yes' if user.password_hash.startswith('$argon2') else 'No'}")
    assert user.password_hash != "strongpassword123"
    assert user.password_hash.startswith("$argon2")
    db.close()
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    run_tests()
