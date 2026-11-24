import os
from fastapi.testclient import TestClient
from main import app
from database.connection import SessionLocal
from models.user import User
from models.resume import Resume
from ml.embeddings.encoder import get_embedding
from ml.services.semantic_analysis import compute_cosine_similarity
from sqlalchemy import select

client = TestClient(app)

def setup_data():
    db = SessionLocal()
    db.execute(Resume.__table__.delete())
    db.execute(User.__table__.delete().where(User.email.in_(["ml_user1@example.com", "ml_user2@example.com"])))
    db.commit()
    
    client.post("/auth/register", json={"name": "ML One", "email": "ml_user1@example.com", "password": "password123"})
    client.post("/auth/register", json={"name": "ML Two", "email": "ml_user2@example.com", "password": "password123"})
    
    u1 = db.execute(select(User).where(User.email == "ml_user1@example.com")).scalar_one()
    u2 = db.execute(select(User).where(User.email == "ml_user2@example.com")).scalar_one()
    
    r1 = Resume(user_id=u1.id, original_filename="res1.pdf", file_type="pdf", file_path="dummy", extracted_text="Experienced in Python, React, and SQL database design.")
    r2 = Resume(user_id=u2.id, original_filename="res2.pdf", file_type="pdf", file_path="dummy", extracted_text="Expert data scientist familiar with Pandas, NumPy, and Machine Learning algorithms.")
    r_empty = Resume(user_id=u1.id, original_filename="empty.pdf", file_type="pdf", file_path="dummy", extracted_text="")
    
    db.add_all([r1, r2, r_empty])
    db.commit()
    
    r1_id, r2_id, r_empty_id = r1.id, r2.id, r_empty.id
    db.close()
    return r1_id, r2_id, r_empty_id

def get_token(email):
    res = client.post("/auth/login", json={"email": email, "password": "password123"})
    return res.json()["access_token"]

def run_tests():
    print("--- Running ML Pipeline Tests ---")
    
    # NLP Unit Tests
    print("\nTEST 1: Model Initialization & Inference")
    emb1 = get_embedding("Hello world")
    emb2 = get_embedding("Hello world")
    assert len(emb1) == 384, "Expected dimension 384"
    
    print("\nTEST 2: Deterministic embeddings")
    # Using np.allclose to handle tiny floating point diffs
    import numpy as np
    assert np.allclose(emb1, emb2), "Same text should produce same embedding"
    
    print("\nTEST 3: Semantic similarity bounds and logic")
    emb_apple = get_embedding("I love eating fresh apples.")
    emb_fruit = get_embedding("Fruits like apples are delicious.")
    emb_car = get_embedding("Driving a fast sports car.")
    
    sim_similar = compute_cosine_similarity(emb_apple, emb_fruit)
    sim_different = compute_cosine_similarity(emb_apple, emb_car)
    
    print(f"Similarity Apple/Fruit: {sim_similar}")
    print(f"Similarity Apple/Car: {sim_different}")
    assert sim_similar > sim_different, "Semantic similarity failed relative bound check"
    
    print("\nTEST 4: Empty text rejection")
    try:
        get_embedding("")
        assert False, "Empty text should be rejected"
    except ValueError:
        pass

    # API Integration Tests
    r1_id, r2_id, r_empty_id = setup_data()
    
    token1 = get_token("ml_user1@example.com")
    token2 = get_token("ml_user2@example.com")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    print("\nTEST 5: Valid job role analysis works")
    res5 = client.post("/ml/analyze-resume", headers=headers1, json={
        "resume_id": r1_id,
        "target_job_role": "Software Engineer"
    })
    assert res5.status_code == 200
    data = res5.json()
    assert data["target_job_role"] == "Software Engineer"
    assert data["embedding_dimension"] == 384
    assert isinstance(data["semantic_similarity"], float)

    print("\nTEST 6: Unsupported job role is rejected")
    res6 = client.post("/ml/analyze-resume", headers=headers1, json={
        "resume_id": r1_id,
        "target_job_role": "Astronaut"
    })
    assert res6.status_code == 422

    print("\nTEST 7: Unauthenticated request -> 401")
    res7 = client.post("/ml/analyze-resume", json={"resume_id": r1_id, "target_job_role": "Software Engineer"})
    assert res7.status_code == 401

    print("\nTEST 8: User A cannot analyze User B's resume")
    res8 = client.post("/ml/analyze-resume", headers=headers1, json={"resume_id": r2_id, "target_job_role": "Data Scientist"})
    assert res8.status_code == 403

    print("\nTEST 9: Invalid resume ID is handled")
    res9 = client.post("/ml/analyze-resume", headers=headers1, json={"resume_id": 99999, "target_job_role": "Software Engineer"})
    assert res9.status_code == 404
    
    print("\nTEST 10: Resume with no extracted text")
    res10 = client.post("/ml/analyze-resume", headers=headers1, json={"resume_id": r_empty_id, "target_job_role": "Software Engineer"})
    assert res10.status_code == 422

    print("\nAll ML tests passed successfully!")

if __name__ == "__main__":
    run_tests()
