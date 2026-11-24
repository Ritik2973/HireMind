from fastapi.testclient import TestClient
from main import app
from database.connection import SessionLocal
from models.user import User

client = TestClient(app)

def setup_user():
    db = SessionLocal()
    db.execute(User.__table__.delete().where(User.email == "swagger@example.com"))
    db.commit()
    
    payload = {
        "name": "Swagger User",
        "email": "swagger@example.com",
        "password": "strongpassword123"
    }
    client.post("/auth/register", json=payload)
    db.close()

def run_tests():
    print("--- Running tests for Swagger OAuth2 Token Endpoint ---")
    setup_user()

    # TEST 1: Valid form-data login
    print("\nTEST 1: Valid form-data login to /auth/token")
    form_data = {
        "username": "swagger@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/auth/token", data=form_data)
    print("Status:", response.status_code)
    assert response.status_code == 200
    resp_json = response.json()
    assert "access_token" in resp_json
    assert resp_json["token_type"] == "bearer"
    assert "password" not in resp_json

    # TEST 2: Incorrect password
    print("\nTEST 2: Incorrect password")
    form_data_bad = {
        "username": "swagger@example.com",
        "password": "wrongpassword"
    }
    response2 = client.post("/auth/token", data=form_data_bad)
    print("Status:", response2.status_code)
    assert response2.status_code == 401

    print("\nAll Swagger auth tests passed successfully!")

if __name__ == "__main__":
    run_tests()
