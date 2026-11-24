from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_tests():
    print("--- Running tests for protected routes ---")

    # 1. Login to get a valid token
    payload_login = {
        "email": "logintest@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/auth/login", json=payload_login)
    assert response.status_code == 200
    token = response.json()["access_token"]
    print("Got access token")

    # TEST 1: Valid JWT
    print("\nTEST 1: Valid JWT")
    res1 = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    print("Status:", res1.status_code)
    print("Response keys:", list(res1.json().keys()))
    assert res1.status_code == 200
    assert "password" not in res1.json()
    assert "password_hash" not in res1.json()
    assert res1.json()["email"] == "logintest@example.com"

    # TEST 2: Without Token
    print("\nTEST 2: Without Token")
    res2 = client.get("/auth/me")
    print("Status:", res2.status_code)
    assert res2.status_code == 401

    # TEST 3: Invalid Token
    print("\nTEST 3: Invalid Token")
    res3 = client.get("/auth/me", headers={"Authorization": f"Bearer invalid_token_here"})
    print("Status:", res3.status_code)
    assert res3.status_code == 401
    
    print("\nAll protected route tests passed successfully!")

if __name__ == "__main__":
    run_tests()
