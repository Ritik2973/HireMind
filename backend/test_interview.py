import os
from fastapi.testclient import TestClient
from main import app
from database.connection import SessionLocal
from models.user import User
from models.interview import InterviewQuestion, InterviewSession, InterviewResponse, Difficulty, InterviewStatus
from sqlalchemy import select
from routers.interview import SUPPORTED_ROLES

SUPPORTED_ROLES.append("Test_Role_SE")

client = TestClient(app)

TEST_ROLE = "Test_Role_SE"
TEST_EMAILS = ["int_user1@example.com", "int_user2@example.com"]

def cleanup_data():
    db = SessionLocal()
    
    # 1. Find test users
    u_ids = db.execute(select(User.id).where(User.email.in_(TEST_EMAILS))).scalars().all()
    
    # 2. Delete their sessions (cascades to responses)
    if u_ids:
        sessions = db.execute(select(InterviewSession).where(InterviewSession.user_id.in_(u_ids))).scalars().all()
        for s in sessions:
            db.delete(s)
        db.commit()
    
    # 3. Delete test questions
    qs = db.execute(select(InterviewQuestion).where(InterviewQuestion.target_job_role == TEST_ROLE)).scalars().all()
    for q in qs:
        db.delete(q)
        
    # 4. Delete test users
    us = db.execute(select(User).where(User.email.in_(TEST_EMAILS))).scalars().all()
    for u in us:
        db.delete(u)
        
    db.commit()
    db.close()

def setup_data():
    cleanup_data() # Ensure clean state before starting
    
    db = SessionLocal()
    
    # Register users natively
    client.post("/auth/register", json={"name": "Int One", "email": TEST_EMAILS[0], "password": "password123"})
    client.post("/auth/register", json={"name": "Int Two", "email": TEST_EMAILS[1], "password": "password123"})
    
    u1 = db.execute(select(User).where(User.email == TEST_EMAILS[0])).scalar_one()
    u2 = db.execute(select(User).where(User.email == TEST_EMAILS[1])).scalar_one()
    
    # Standard evaluation payload for test questions
    eval_meta = {
        "expected_answer": "The quick brown fox jumps over the lazy dog.",
        "key_concepts": ["quick", "brown", "fox", "jumps", "lazy", "dog"],
        "rubric_criteria": ["Mentions fox", "Mentions dog"]
    }
    
    # Seed specific questions for testing transitions
    q_data = [
        ("EASY 1", "EASY"), ("MEDIUM 1", "MEDIUM"), ("HARD 1", "HARD"),
        ("EASY 2", "EASY"), ("MEDIUM 2", "MEDIUM"), ("HARD 2", "HARD"),
        ("HARD 3", "HARD"), ("MEDIUM 3", "MEDIUM")
    ]
    
    questions = []
    for q_text, diff in q_data:
        questions.append(InterviewQuestion(
            target_job_role=TEST_ROLE, 
            category="Technical", 
            difficulty=diff, 
            question_text=q_text,
            **eval_meta
        ))

    db.add_all(questions)
    db.commit()
    
    u1_id, u2_id = u1.id, u2.id
    db.close()
    return u1_id, u2_id

def get_token(email):
    res = client.post("/auth/login", json={"email": email, "password": "password123"})
    return res.json()["access_token"]

def run_tests():
    print("--- Running Adaptive Interview Tests with AI Evaluation ---")
    
    try:
        u1_id, u2_id = setup_data()
        token1 = get_token(TEST_EMAILS[0])
        token2 = get_token(TEST_EMAILS[1])
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        # 1. Starting an interview with a valid role works.
        print("\nTEST: Start interview (MEDIUM default)")
        res = client.post("/interviews/start", headers=headers1, json={"target_job_role": TEST_ROLE})
        assert res.status_code == 200
        data = res.json()
        session_id = data["id"]
        assert data["current_difficulty"] == "MEDIUM"
        q_id_1 = data["current_question"]["id"]
        
        # 2. Client-supplied score is rejected via strict Pydantic validation
        print("\nTEST: Submitting client performance_score -> 422")
        res_bad = client.post(f"/interviews/{session_id}/answer", headers=headers1, json={
            "question_id": q_id_1,
            "answer_text": "Answer",
            "performance_score": 100
        })
        assert res_bad.status_code == 422

        # 2a. Empty answer rejected
        print("\nTEST: Empty answer rejected -> 422")
        res_empty = client.post(f"/interviews/{session_id}/answer", headers=headers1, json={
            "question_id": q_id_1,
            "answer_text": ""
        })
        assert res_empty.status_code == 422

        # 2b. Ownership protection
        print("\nTEST: Ownership protection (User 2 accesses User 1's session) -> 403")
        res_auth = client.post(f"/interviews/{session_id}/answer", headers=headers2, json={
            "question_id": q_id_1,
            "answer_text": "Answer"
        })
        assert res_auth.status_code == 403

        # 3. High AI Score -> Increases Difficulty
        print("\nTEST: AI Evaluation high score -> HARD")
        # Submitting identical text to expected yields near 100 score
        res = client.post(f"/interviews/{session_id}/answer", headers=headers1, json={
            "question_id": q_id_1,
            "answer_text": "The quick brown fox jumps over the lazy dog."
        })
        if res.status_code != 200:
            print("ERROR", res.json())
        assert res.status_code == 200
        data = res.json()
        assert data["latest_evaluation"]["overall_score"] > 85
        assert data["current_difficulty"] == "HARD"
        q_id_2 = data["current_question"]["id"]
        
        # 4. Medium AI Score -> Keeps Difficulty
        print("\nTEST: AI Evaluation medium score -> HARD (unchanged)")
        # Missing some keywords to get an intermediate score
        res = client.post(f"/interviews/{session_id}/answer", headers=headers1, json={
            "question_id": q_id_2,
            "answer_text": "A brown fox jumps over a dog sometimes."
        })
        assert res.status_code == 200
        data = res.json()
        eval_score = data["latest_evaluation"]["overall_score"]
        assert 60 <= eval_score < 80, f"Expected 60-79, got {eval_score}"
        assert data["current_difficulty"] == "HARD"
        q_id_3 = data["current_question"]["id"]

        # 5. Low AI Score -> Decreases Difficulty
        print("\nTEST: AI Evaluation low score -> MEDIUM")
        res = client.post(f"/interviews/{session_id}/answer", headers=headers1, json={
            "question_id": q_id_3,
            "answer_text": "I really like eating pizza and pasta."
        })
        assert res.status_code == 200
        data = res.json()
        assert data["latest_evaluation"]["overall_score"] < 60
        assert data["current_difficulty"] == "MEDIUM"
        q_id_4 = data["current_question"]["id"]

        # Check DB Persistence
        print("\nTEST: Evaluation fields are persisted in DB")
        db = SessionLocal()
        responses = db.execute(select(InterviewResponse).where(InterviewResponse.session_id == session_id).order_by(InterviewResponse.id.asc())).scalars().all()
        assert len(responses) == 3
        # First response should have score > 85
        assert responses[0].performance_score > 85
        assert responses[0].semantic_similarity is not None
        assert responses[0].concept_coverage is not None
        assert responses[0].completeness_score is not None
        assert responses[0].feedback is not None
        db.close()

        # Drop to EASY
        res = client.post(f"/interviews/{session_id}/answer", headers=headers1, json={
            "question_id": q_id_4,
            "answer_text": "Irrelevant nonsense."
        })
        data = res.json()
        assert data["current_difficulty"] == "EASY"
        q_id_5 = data["current_question"]["id"]

        # Exhaustion Test
        print("\nTEST: Exhaustion -> COMPLETED")
        current_q_id = q_id_5
        for _ in range(20):
            res = client.post(f"/interviews/{session_id}/answer", headers=headers1, json={
                "question_id": current_q_id,
                "answer_text": "The quick brown fox jumps over the lazy dog."
            })
            if res.json().get("status") == "COMPLETED":
                break
            current_q_id = res.json()["current_question"]["id"]
        else:
            assert False, "Exhaustion test hung."

        final_data = client.get(f"/interviews/{session_id}", headers=headers1).json()
        assert final_data["status"] == "COMPLETED"
        
        # Completed session protection
        print("\nTEST: Completed session protection -> 400")
        res_completed = client.post(f"/interviews/{session_id}/answer", headers=headers1, json={
            "question_id": current_q_id,
            "answer_text": "Trying to answer after completion."
        })
        assert res_completed.status_code == 400
        # The engine throws "does not match" because current_question_id is None, OR "completed"
        detail_msg = res_completed.json()["detail"].lower()
        assert "completed" in detail_msg or "does not match" in detail_msg
        
        print("\nAll Interview tests passed successfully!")
    finally:
        # Guarantee cleanup even if tests fail
        cleanup_data()

if __name__ == "__main__":
    run_tests()

