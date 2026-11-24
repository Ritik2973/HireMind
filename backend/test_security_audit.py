"""
HireMind Milestone 11: Security & Error Handling Verification Suite.

Validates:
1. Malformed JWT with non-integer subject claim returns 401 (not 500).
2. Tampered JWT signature returns 401.
3. Expired JWT returns 401.
4. Missing authentication returns 401.
5. Cross-user data isolation across Resumes, Interviews, ML Analysis, and Career Readiness reports (returns 403).
6. File upload validations: non-PDF rejection (400), oversized >5MB rejection (413).
7. Submitting answer to completed interview session returns 400 (not 500).
"""

import sys
import os
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from fastapi.testclient import TestClient

# Ensure backend root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import app
from database.connection import SessionLocal
import models.user
from models.user import User
from models.resume import Resume
from models.interview import InterviewSession, InterviewQuestion, InterviewResponse, InterviewStatus
from models.readiness import CareerReadinessReport
from security.jwt import SECRET_KEY, ALGORITHM, create_access_token

client = TestClient(app)


def run_security_audit_tests():
    print("\n" + "=" * 60)
    print("RUNNING MILESTONE 11: SECURITY & ERROR HANDLING AUDIT TESTS")
    print("=" * 60)

    db = SessionLocal()

    created_user_ids = []
    created_session_ids = []
    created_resume_ids = []
    created_report_ids = []

    try:
        # Create test users A and B
        u_suffix_a = uuid.uuid4().hex[:8]
        u_suffix_b = uuid.uuid4().hex[:8]

        user_a = User(
            name=f"Security User A {u_suffix_a}",
            email=f"sec_a_{u_suffix_a}@example.com",
            password_hash="argon2_fake_hash_value",
            target_job_role="Software Engineer"
        )
        user_b = User(
            name=f"Security User B {u_suffix_b}",
            email=f"sec_b_{u_suffix_b}@example.com",
            password_hash="argon2_fake_hash_value",
            target_job_role="Software Engineer"
        )
        db.add(user_a)
        db.add(user_b)
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)
        created_user_ids.extend([user_a.id, user_b.id])

        token_a = create_access_token({"sub": str(user_a.id)})
        token_b = create_access_token({"sub": str(user_b.id)})

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # -------------------------------------------------------------
        # TEST 1: Malformed JWT sub claim (non-integer string)
        # -------------------------------------------------------------
        print("\n[TEST 1] Malformed JWT: non-integer sub claim should return 401 (not 500)")
        malformed_token = jwt.encode(
            {"sub": "non_integer_username_attack", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        res1 = client.get("/users/me", headers={"Authorization": f"Bearer {malformed_token}"})
        assert res1.status_code == 401, f"Expected 401 for malformed sub, got {res1.status_code}: {res1.text}"
        print("  -> PASS: Malformed sub safely rejected with 401 Unauthorized.")

        # -------------------------------------------------------------
        # TEST 2: Tampered JWT signature
        # -------------------------------------------------------------
        print("\n[TEST 2] Tampered JWT signature should return 401")
        tampered_token = jwt.encode(
            {"sub": str(user_a.id), "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "completely_wrong_secret_key_999",
            algorithm=ALGORITHM
        )
        res2 = client.get("/users/me", headers={"Authorization": f"Bearer {tampered_token}"})
        assert res2.status_code == 401, f"Expected 401 for tampered signature, got {res2.status_code}: {res2.text}"
        print("  -> PASS: Tampered token safely rejected with 401 Unauthorized.")

        # -------------------------------------------------------------
        # TEST 3: Expired JWT token
        # -------------------------------------------------------------
        print("\n[TEST 3] Expired JWT token should return 401")
        expired_token = jwt.encode(
            {"sub": str(user_a.id), "exp": datetime.now(timezone.utc) - timedelta(minutes=15)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        res3 = client.get("/users/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert res3.status_code == 401, f"Expected 401 for expired token, got {res3.status_code}: {res3.text}"
        print("  -> PASS: Expired token safely rejected with 401 Unauthorized.")

        # -------------------------------------------------------------
        # TEST 4: Missing authentication header
        # -------------------------------------------------------------
        print("\n[TEST 4] Missing auth header should return 401")
        res4 = client.get("/users/me")
        assert res4.status_code == 401, f"Expected 401 for missing auth, got {res4.status_code}"
        print("  -> PASS: Unauthenticated access rejected with 401 Unauthorized.")

        # -------------------------------------------------------------
        # TEST 5: Cross-User Data Isolation
        # -------------------------------------------------------------
        print("\n[TEST 5] Cross-user isolation: User B cannot access User A's data")
        
        # User A's resume
        resume_a = Resume(
            user_id=user_a.id,
            original_filename="user_a_resume.pdf",
            file_type="application/pdf",
            file_path="uploads/fake_a.pdf",
            extracted_text="Python React SQL Docker",
            skills=["Python", "React", "SQL"]
        )
        db.add(resume_a)

        # User A's interview session
        session_a = InterviewSession(
            user_id=user_a.id,
            target_job_role="Software Engineer",
            current_difficulty="MEDIUM",
            status="IN_PROGRESS"
        )
        db.add(session_a)
        db.commit()
        db.refresh(resume_a)
        db.refresh(session_a)
        created_resume_ids.append(resume_a.id)
        created_session_ids.append(session_a.id)

        # 5a. User B attempts GET /resumes/{resume_a.id} -> 403
        res5a = client.get(f"/resumes/{resume_a.id}", headers=headers_b)
        assert res5a.status_code == 403, f"Expected 403 for cross-user resume access, got {res5a.status_code}"
        print("  -> PASS: User B forbidden from reading User A's resume (403).")

        # 5b. User B attempts POST /ml/analyze-resume on User A's resume -> 403
        res5b = client.post(
            "/ml/analyze-resume",
            headers=headers_b,
            json={"resume_id": resume_a.id, "target_job_role": "Software Engineer"}
        )
        assert res5b.status_code == 403, f"Expected 403 for cross-user ML analysis, got {res5b.status_code}"
        print("  -> PASS: User B forbidden from triggering ML analysis on User A's resume (403).")

        # 5c. User B attempts GET /interviews/{session_a.id} -> 403
        res5c = client.get(f"/interviews/{session_a.id}", headers=headers_b)
        assert res5c.status_code == 403, f"Expected 403 for cross-user interview read, got {res5c.status_code}"
        print("  -> PASS: User B forbidden from reading User A's interview (403).")

        # 5d. User B attempts POST /interviews/{session_a.id}/answer -> 403
        res5d = client.post(
            f"/interviews/{session_a.id}/answer",
            headers=headers_b,
            json={"question_id": 1, "answer_text": "Unauthorized answer attempt"}
        )
        assert res5d.status_code == 403, f"Expected 403 for cross-user answer submission, got {res5d.status_code}"
        print("  -> PASS: User B forbidden from submitting answer to User A's session (403).")

        # User A's career readiness report
        report_a = CareerReadinessReport(
            user_id=user_a.id,
            interview_session_id=session_a.id,
            resume_id=resume_a.id,
            target_job_role="Software Engineer",
            technical_score=85.0,
            problem_solving_score=80.0,
            communication_score=75.0,
            behavioral_score=70.0,
            resume_skill_match_score=80.0,
            interview_performance_score=80.0,
            overall_readiness_score=78.5
        )
        db.add(report_a)
        db.commit()
        db.refresh(report_a)
        created_report_ids.append(report_a.id)

        # 5e. User B attempts GET /career-readiness/{report_a.id} -> 403
        res5e = client.get(f"/career-readiness/{report_a.id}", headers=headers_b)
        assert res5e.status_code == 403, f"Expected 403 for cross-user readiness report read, got {res5e.status_code}"
        print("  -> PASS: User B forbidden from accessing User A's readiness report (403).")

        # -------------------------------------------------------------
        # TEST 6: Resume Upload Restrictions
        # -------------------------------------------------------------
        print("\n[TEST 6] Resume upload restrictions: Non-PDF and Oversized files")
        
        # 6a. Non-PDF upload rejection -> 422 (Only PDF files are supported)
        res6a = client.post(
            "/resumes/upload",
            headers=headers_a,
            files={"file": ("malicious_script.sh", b"echo 'hack'", "text/plain")}
        )
        assert res6a.status_code == 422, f"Expected 422 for non-PDF, got {res6a.status_code}"
        print("  -> PASS: Non-PDF file upload rejected with 422 Unprocessable Entity.")

        # 6b. Oversized upload rejection -> 413 (> 5MB)
        oversized_data = b"0" * (5 * 1024 * 1024 + 1024)
        res6b = client.post(
            "/resumes/upload",
            headers=headers_a,
            files={"file": ("huge_resume.pdf", oversized_data, "application/pdf")}
        )
        assert res6b.status_code == 413, f"Expected 413 for oversized file, got {res6b.status_code}"
        print("  -> PASS: Oversized file (>5MB) rejected with 413 Payload Too Large.")

        # -------------------------------------------------------------
        # TEST 7: Submitting Answer to Completed Interview Session
        # -------------------------------------------------------------
        print("\n[TEST 7] Submitting answer to completed interview session returns 400 (not 500)")
        
        # Mark session_a as COMPLETED and clear current_question_id
        session_a.status = "COMPLETED"
        session_a.current_question_id = None
        db.commit()

        res7 = client.post(
            f"/interviews/{session_a.id}/answer",
            headers=headers_a,
            json={"question_id": 999, "answer_text": "Answering completed session"}
        )
        assert res7.status_code == 400, f"Expected 400 for completed session answer, got {res7.status_code}: {res7.text}"
        assert "already completed" in res7.json().get("detail", "").lower()
        print("  -> PASS: Completed session answer rejected with 400 Bad Request.")

        print("\n" + "=" * 60)
        print("ALL SECURITY & ERROR HANDLING TESTS PASSED (7/7)")
        print("=" * 60)

    finally:
        # Clean up ONLY test-created artifacts
        for rep_id in created_report_ids:
            db.query(CareerReadinessReport).filter(CareerReadinessReport.id == rep_id).delete()
        for sess_id in created_session_ids:
            db.query(InterviewResponse).filter(InterviewResponse.session_id == sess_id).delete()
            db.query(InterviewSession).filter(InterviewSession.id == sess_id).delete()
        for res_id in created_resume_ids:
            db.query(Resume).filter(Resume.id == res_id).delete()
        for u_id in created_user_ids:
            db.query(User).filter(User.id == u_id).delete()
        db.commit()
        db.close()


if __name__ == "__main__":
    run_security_audit_tests()
