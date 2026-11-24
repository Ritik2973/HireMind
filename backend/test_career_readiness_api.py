"""
Backend API Tests for HireMind Milestone 9: Career Readiness Analyzer Endpoints.

Tests:
1. Unauthenticated requests (POST /generate and GET /{report_id}) -> 401
2. Invalid session ID -> 404
3. Invalid resume ID -> 404
4. Incomplete interview (status != COMPLETED) -> 400
5. Another user's session or resume -> 403
6. Successful report generation -> 200 with complete report schema
7. Successful report retrieval -> 200 with matching report data
8. Another user's report access -> 403
"""

import sys
import os
import uuid
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import app
from database.connection import SessionLocal
from models.user import User
from models.resume import Resume
from models.interview import InterviewSession, InterviewQuestion, InterviewResponse
from models.readiness import CareerReadinessReport
from security.jwt import create_access_token

client = TestClient(app)


def run_api_tests():
    print("\n==================================================")
    print("RUNNING CAREER READINESS API ENDPOINT TESTS")
    print("==================================================")
    
    db = SessionLocal()
    
    created_user_ids = []
    created_session_ids = []
    created_resume_ids = []
    created_question_ids = []
    created_report_ids = []
    
    try:
        # Create User A and User B
        uid_a = str(uuid.uuid4())
        uid_b = str(uuid.uuid4())
        
        user_a = User(name="User A", email=f"user_a_{uid_a}@example.com", password_hash="hash")
        user_b = User(name="User B", email=f"user_b_{uid_b}@example.com", password_hash="hash")
        db.add_all([user_a, user_b])
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)
        created_user_ids.extend([user_a.id, user_b.id])
        
        token_a = create_access_token(data={"sub": str(user_a.id)})
        token_b = create_access_token(data={"sub": str(user_b.id)})
        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}
        
        # ----------------------------------------------------
        # 1. Unauthenticated request tests
        # ----------------------------------------------------
        print("\n[TEST 1] Unauthenticated request verification...")
        res_unauth_post = client.post("/career-readiness/generate", json={"interview_session_id": 1, "resume_id": 1})
        assert res_unauth_post.status_code == 401, f"Expected 401, got {res_unauth_post.status_code}"
        
        res_unauth_get = client.get("/career-readiness/1")
        assert res_unauth_get.status_code == 401, f"Expected 401, got {res_unauth_get.status_code}"
        print("PASS: Unauthenticated requests returned 401 Unauthorized.")
        
        # Set up resumes
        resume_a = Resume(
            user_id=user_a.id,
            extracted_text="Python FastAPI PostgreSQL Docker Git Software Engineer",
            original_filename="resume_a.pdf",
            file_type="pdf",
            file_path="tmp/resume_a.pdf"
        )
        resume_b = Resume(
            user_id=user_b.id,
            extracted_text="Java Spring Boot Kubernetes",
            original_filename="resume_b.pdf",
            file_type="pdf",
            file_path="tmp/resume_b.pdf"
        )
        db.add_all([resume_a, resume_b])
        db.commit()
        created_resume_ids.extend([resume_a.id, resume_b.id])
        
        # Set up completed session for user A with full category responses
        session_a = InterviewSession(user_id=user_a.id, target_job_role="Software Engineer", status="COMPLETED")
        db.add(session_a)
        db.commit()
        created_session_ids.append(session_a.id)
        
        # Questions & responses for User A
        q_tech = InterviewQuestion(target_job_role="Software Engineer", category="Technical", question_text="Tech Q", difficulty="MEDIUM")
        q_ps = InterviewQuestion(target_job_role="Software Engineer", category="Problem Solving", question_text="PS Q", difficulty="MEDIUM")
        q_beh = InterviewQuestion(target_job_role="Software Engineer", category="Behavioral", question_text="Beh Q", difficulty="MEDIUM")
        db.add_all([q_tech, q_ps, q_beh])
        db.commit()
        created_question_ids.extend([q_tech.id, q_ps.id, q_beh.id])
        
        r_tech = InterviewResponse(session_id=session_a.id, question_id=q_tech.id, answer_text="Ans Tech", performance_score=85.0, semantic_similarity=85.0, concept_coverage=85.0, completeness_score=85.0)
        r_ps = InterviewResponse(session_id=session_a.id, question_id=q_ps.id, answer_text="Ans PS", performance_score=75.0, semantic_similarity=75.0, concept_coverage=75.0, completeness_score=75.0)
        r_beh = InterviewResponse(session_id=session_a.id, question_id=q_beh.id, answer_text="Ans Beh", performance_score=90.0, semantic_similarity=90.0, concept_coverage=90.0, completeness_score=90.0)
        db.add_all([r_tech, r_ps, r_beh])
        db.commit()
        
        # ----------------------------------------------------
        # 2. Invalid session test
        # ----------------------------------------------------
        print("\n[TEST 2] Invalid session verification...")
        res_inv_session = client.post(
            "/career-readiness/generate",
            json={"interview_session_id": 999999, "resume_id": resume_a.id},
            headers=headers_a
        )
        assert res_inv_session.status_code == 404, f"Expected 404, got {res_inv_session.status_code}: {res_inv_session.text}"
        assert "Interview session not found" in res_inv_session.json()["detail"]
        print("PASS: Invalid session returned 404 Not Found.")
        
        # ----------------------------------------------------
        # 3. Invalid resume test
        # ----------------------------------------------------
        print("\n[TEST 3] Invalid resume verification...")
        res_inv_resume = client.post(
            "/career-readiness/generate",
            json={"interview_session_id": session_a.id, "resume_id": 999999},
            headers=headers_a
        )
        assert res_inv_resume.status_code == 404, f"Expected 404, got {res_inv_resume.status_code}: {res_inv_resume.text}"
        assert "Resume not found" in res_inv_resume.json()["detail"]
        print("PASS: Invalid resume returned 404 Not Found.")
        
        # ----------------------------------------------------
        # 4. Incomplete interview test
        # ----------------------------------------------------
        print("\n[TEST 4] Incomplete interview verification...")
        session_incomplete = InterviewSession(user_id=user_a.id, target_job_role="Software Engineer", status="IN_PROGRESS")
        db.add(session_incomplete)
        db.commit()
        created_session_ids.append(session_incomplete.id)
        
        res_incomp = client.post(
            "/career-readiness/generate",
            json={"interview_session_id": session_incomplete.id, "resume_id": resume_a.id},
            headers=headers_a
        )
        assert res_incomp.status_code == 400, f"Expected 400, got {res_incomp.status_code}: {res_incomp.text}"
        assert "incomplete interview" in res_incomp.json()["detail"]
        print("PASS: Incomplete interview returned 400 Bad Request.")
        
        # 4b. Unsupported job role test
        print("\n[TEST 4b] Unsupported job role verification...")
        session_bad_role = InterviewSession(user_id=user_a.id, target_job_role="Unsupported Role 999", status="COMPLETED")
        db.add(session_bad_role)
        db.commit()
        created_session_ids.append(session_bad_role.id)
        
        res_bad_role = client.post(
            "/career-readiness/generate",
            json={"interview_session_id": session_bad_role.id, "resume_id": resume_a.id},
            headers=headers_a
        )
        assert res_bad_role.status_code == 400, f"Expected 400, got {res_bad_role.status_code}: {res_bad_role.text}"
        assert "Invalid target job role" in res_bad_role.json()["detail"] or "not currently supported" in res_bad_role.json()["detail"]
        print("PASS: Unsupported job role returned 400 Bad Request.")
        
        # 4c. Missing AI evaluation data test (missing concept_coverage)
        print("\n[TEST 4c] Missing evaluation data verification...")
        session_missing_data = InterviewSession(user_id=user_a.id, target_job_role="Software Engineer", status="COMPLETED")
        db.add(session_missing_data)
        db.commit()
        created_session_ids.append(session_missing_data.id)
        
        # Add response missing concept_coverage
        r_incomplete_eval = InterviewResponse(
            session_id=session_missing_data.id, question_id=q_tech.id, answer_text="Ans",
            performance_score=80.0, semantic_similarity=80.0, concept_coverage=None, completeness_score=80.0
        )
        db.add(r_incomplete_eval)
        db.commit()
        
        res_missing_eval = client.post(
            "/career-readiness/generate",
            json={"interview_session_id": session_missing_data.id, "resume_id": resume_a.id},
            headers=headers_a
        )
        assert res_missing_eval.status_code == 400, f"Expected 400, got {res_missing_eval.status_code}: {res_missing_eval.text}"
        assert "Required AI evaluation data is missing" in res_missing_eval.json()["detail"]
        print("PASS: Missing evaluation data returned 400 Bad Request.")
        
        # ----------------------------------------------------
        # 5. Cross-user session or resume test
        # ----------------------------------------------------
        print("\n[TEST 5] Cross-user session / resume ownership verification...")
        session_b = InterviewSession(user_id=user_b.id, target_job_role="Software Engineer", status="COMPLETED")
        db.add(session_b)
        db.commit()
        created_session_ids.append(session_b.id)
        
        # User A trying to use User B's session
        res_cross_session = client.post(
            "/career-readiness/generate",
            json={"interview_session_id": session_b.id, "resume_id": resume_a.id},
            headers=headers_a
        )
        assert res_cross_session.status_code == 403, f"Expected 403, got {res_cross_session.status_code}: {res_cross_session.text}"
        assert "Not authorized to access this interview session" in res_cross_session.json()["detail"]
        
        # User A trying to use User B's resume
        res_cross_resume = client.post(
            "/career-readiness/generate",
            json={"interview_session_id": session_a.id, "resume_id": resume_b.id},
            headers=headers_a
        )
        assert res_cross_resume.status_code == 403, f"Expected 403, got {res_cross_resume.status_code}: {res_cross_resume.text}"
        assert "Not authorized to access this resume" in res_cross_resume.json()["detail"]
        print("PASS: Cross-user session and resume access returned 403 Forbidden.")
        
        # ----------------------------------------------------
        # 6. Successful report generation test
        # ----------------------------------------------------
        print("\n[TEST 6] Successful report generation verification...")
        res_success = client.post(
            "/career-readiness/generate",
            json={"interview_session_id": session_a.id, "resume_id": resume_a.id},
            headers=headers_a
        )
        assert res_success.status_code == 200, f"Expected 200, got {res_success.status_code}: {res_success.text}"
        data = res_success.json()
        
        assert "id" in data
        assert "report_id" in data
        assert data["id"] == data["report_id"]
        report_id = data["id"]
        created_report_ids.append(report_id)
        
        assert data["target_job_role"] == "Software Engineer"
        assert data["technical_score"] == 85.0
        assert data["problem_solving_score"] == 75.0
        assert data["behavioral_score"] == 90.0
        assert data["interview_performance_score"] == round((85.0 + 75.0 + 90.0) / 3, 2)
        assert "overall_readiness_score" in data
        assert isinstance(data["overall_readiness_score"], float)
        assert 0.0 <= data["overall_readiness_score"] <= 100.0
        assert "generated_at" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert "component_recommendations" in data
        assert isinstance(data["component_recommendations"], dict)
        assert "technical" in data["component_recommendations"]
        assert "problem_solving" in data["component_recommendations"]
        assert "communication" in data["component_recommendations"]
        assert "behavioral" in data["component_recommendations"]
        assert "resume_skill_match" in data["component_recommendations"]
        assert "interview_performance" in data["component_recommendations"]
        print(f"PASS: Report {report_id} successfully generated with overall score {data['overall_readiness_score']}.")
        
        # ----------------------------------------------------
        # 7. Successful report retrieval test
        # ----------------------------------------------------
        print("\n[TEST 7] Successful report retrieval verification...")
        res_get = client.get(f"/career-readiness/{report_id}", headers=headers_a)
        assert res_get.status_code == 200, f"Expected 200, got {res_get.status_code}: {res_get.text}"
        get_data = res_get.json()
        assert get_data["id"] == report_id
        assert get_data["target_job_role"] == "Software Engineer"
        assert get_data["overall_readiness_score"] == data["overall_readiness_score"]
        print("PASS: Report retrieved successfully with matching data.")

        # Test GET /career-readiness/latest
        print("\n[TEST 7b] Latest report retrieval verification (/latest)...")
        res_latest = client.get("/career-readiness/latest", headers=headers_a)
        assert res_latest.status_code == 200, f"Expected 200, got {res_latest.status_code}: {res_latest.text}"
        assert res_latest.json()["id"] == report_id
        print("PASS: Latest report retrieved successfully via /latest.")

        # Test GET /career-readiness/session/{session_id}
        print("\n[TEST 7c] Session report retrieval verification (/session/{session_id})...")
        res_sess = client.get(f"/career-readiness/session/{session_a.id}", headers=headers_a)
        assert res_sess.status_code == 200, f"Expected 200, got {res_sess.status_code}: {res_sess.text}"
        assert res_sess.json()["id"] == report_id
        print("PASS: Session report retrieved successfully via /session/{session_id}.")
        
        # ----------------------------------------------------
        # 8. Another user's report access test
        # ----------------------------------------------------
        print("\n[TEST 8] Another user's report access verification...")
        res_cross_report = client.get(f"/career-readiness/{report_id}", headers=headers_b)
        assert res_cross_report.status_code == 403, f"Expected 403, got {res_cross_report.status_code}: {res_cross_report.text}"
        assert "Not authorized to access this report" in res_cross_report.json()["detail"]
        print("PASS: Accessing another user's report returned 403 Forbidden.")
        
        # Also test non-existent report ID
        res_nonexistent = client.get("/career-readiness/999999", headers=headers_a)
        assert res_nonexistent.status_code == 404
        assert "Career readiness report not found" in res_nonexistent.json()["detail"]
        print("PASS: Non-existent report returned 404 Not Found.")
        
        print("\n==================================================")
        print("ALL CAREER READINESS API TESTS PASSED SUCCESSFULLY!")
        print("==================================================")
        
    finally:
        db.rollback()
        for rep_id in created_report_ids:
            db.execute(CareerReadinessReport.__table__.delete().where(CareerReadinessReport.id == rep_id))
        for sid in created_session_ids:
            db.execute(InterviewResponse.__table__.delete().where(InterviewResponse.session_id == sid))
            db.execute(InterviewSession.__table__.delete().where(InterviewSession.id == sid))
        if created_question_ids:
            db.execute(InterviewQuestion.__table__.delete().where(InterviewQuestion.id.in_(created_question_ids)))
        for rid in created_resume_ids:
            db.execute(Resume.__table__.delete().where(Resume.id == rid))
        for uid in created_user_ids:
            db.execute(User.__table__.delete().where(User.id == uid))
        db.commit()
        db.close()


if __name__ == "__main__":
    run_api_tests()
