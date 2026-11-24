"""
Backend API Tests for HireMind Milestone 10: Dashboard & Analytics Endpoints.

Tests:
1. Unauthorized request (GET /analytics/dashboard without token) -> 401
2. Empty account (User with no interviews, resumes, or reports) -> 200 with clean None/0 defaults
3. User with resume only -> 200 with resume stats and clean None/0 interview/readiness stats
4. Multiple interview sessions & correct category score aggregation -> 200 with verified averages
5. Multiple Career Readiness reports -> 200 with verified latest report, tier, and progression history
6. Cross-user data isolation -> User B cannot see User A's interviews, resumes, or reports
"""

import sys
import os
import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import app
from database.connection import SessionLocal
import models.user
from models.user import User
from models.resume import Resume
from models.interview import InterviewSession, InterviewQuestion, InterviewResponse
from models.readiness import CareerReadinessReport
from security.jwt import create_access_token

client = TestClient(app)


def run_analytics_tests():
    print("\n==================================================")
    print("RUNNING DASHBOARD & ANALYTICS API TESTS")
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

        user_a = User(
            name="Alice Analytics",
            email=f"alice_{uid_a}@example.com",
            password_hash="hash_a",
            target_job_role="Software Engineer"
        )
        user_b = User(
            name="Bob Empty",
            email=f"bob_{uid_b}@example.com",
            password_hash="hash_b",
            target_job_role="Data Scientist"
        )
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
        # 1. Unauthorized access test
        # ----------------------------------------------------
        print("\n[TEST 1] Unauthorized access verification...")
        res_unauth = client.get("/analytics/dashboard")
        assert res_unauth.status_code == 401, f"Expected 401, got {res_unauth.status_code}"
        print("PASS: Request without token returned 401 Unauthorized.")

        # ----------------------------------------------------
        # 2. Empty account test (User B before any data)
        # ----------------------------------------------------
        print("\n[TEST 2] Empty account dashboard access...")
        res_empty = client.get("/analytics/dashboard", headers=headers_b)
        assert res_empty.status_code == 200, f"Expected 200, got {res_empty.status_code}: {res_empty.text}"
        data_b = res_empty.json()

        assert data_b["user_id"] == user_b.id
        assert data_b["user_name"] == "Bob Empty"
        assert data_b["target_job_role"] == "Data Scientist"

        # Interview stats check
        assert data_b["interview_stats"]["total_sessions"] == 0
        assert data_b["interview_stats"]["completed_interviews"] == 0
        assert data_b["interview_stats"]["in_progress_interviews"] == 0
        assert data_b["interview_stats"]["total_responses"] == 0
        assert data_b["interview_stats"]["average_score"] is None

        # Category performance check
        assert data_b["category_performance"]["technical_average"] is None
        assert data_b["category_performance"]["problem_solving_average"] is None
        assert data_b["category_performance"]["behavioral_average"] is None

        # Resume stats check
        assert data_b["resume_stats"]["resume_count"] == 0
        assert data_b["resume_stats"]["latest_resume"] is None
        assert data_b["resume_stats"]["extracted_skills"] == []

        # Career readiness check
        assert data_b["career_readiness"]["latest_report"] is None
        assert data_b["career_readiness"]["overall_readiness_score"] is None
        assert data_b["career_readiness"]["readiness_tier"] is None
        assert data_b["career_readiness"]["history"] == []

        # Recent interviews check
        assert data_b["recent_interviews"] == []
        print("PASS: Empty account returned clean 200 with null metrics and 0 counts.")

        # ----------------------------------------------------
        # 3. User with resume only test
        # ----------------------------------------------------
        print("\n[TEST 3] User with resume only...")
        resume_b = Resume(
            user_id=user_b.id,
            original_filename="bob_resume.pdf",
            file_type="application/pdf",
            file_path="tmp/bob_resume.pdf",
            extracted_text="Python Pandas SQL Machine Learning",
            skills=["Python", "Pandas", "SQL", "Machine Learning"]
        )
        db.add(resume_b)
        db.commit()
        db.refresh(resume_b)
        created_resume_ids.append(resume_b.id)

        res_resume_only = client.get("/analytics/dashboard", headers=headers_b)
        assert res_resume_only.status_code == 200
        data_b_res = res_resume_only.json()
        assert data_b_res["resume_stats"]["resume_count"] == 1
        assert data_b_res["resume_stats"]["latest_resume"]["id"] == resume_b.id
        assert data_b_res["resume_stats"]["latest_resume"]["original_filename"] == "bob_resume.pdf"
        assert data_b_res["resume_stats"]["latest_resume"]["skills_count"] == 4
        assert data_b_res["resume_stats"]["extracted_skills"] == ["Python", "Pandas", "SQL", "Machine Learning"]
        # Interviews and readiness must still be null/empty
        assert data_b_res["interview_stats"]["total_sessions"] == 0
        assert data_b_res["career_readiness"]["latest_report"] is None
        print("PASS: User with resume correctly displays resume stats and null interview metrics.")

        # ----------------------------------------------------
        # 4. Multiple interview sessions & Category score aggregation
        # ----------------------------------------------------
        print("\n[TEST 4] Multiple interview sessions & category score aggregation...")
        # Create test questions for User A
        q_tech = InterviewQuestion(
            target_job_role="Software Engineer",
            question_text="Explain Python GIL",
            category="Technical",
            difficulty="MEDIUM"
        )
        q_ps = InterviewQuestion(
            target_job_role="Software Engineer",
            question_text="Design a rate limiter",
            category="Problem Solving",
            difficulty="MEDIUM"
        )
        q_beh = InterviewQuestion(
            target_job_role="Software Engineer",
            question_text="Describe a conflict with a peer",
            category="Behavioral",
            difficulty="MEDIUM"
        )
        db.add_all([q_tech, q_ps, q_beh])
        db.commit()
        created_question_ids.extend([q_tech.id, q_ps.id, q_beh.id])

        # Session 1: COMPLETED
        now = datetime.now(timezone.utc)
        session_a1 = InterviewSession(
            user_id=user_a.id,
            target_job_role="Software Engineer",
            status="COMPLETED",
            current_difficulty="MEDIUM",
            started_at=now - timedelta(hours=3),
            completed_at=now - timedelta(hours=2)
        )
        # Session 2: IN_PROGRESS
        session_a2 = InterviewSession(
            user_id=user_a.id,
            target_job_role="Software Engineer",
            status="IN_PROGRESS",
            current_difficulty="HARD",
            started_at=now - timedelta(hours=1),
            completed_at=None
        )
        db.add_all([session_a1, session_a2])
        db.commit()
        created_session_ids.extend([session_a1.id, session_a2.id])

        # Responses for Session 1:
        # Technical: 80.0
        # Problem Solving: 70.0
        # Behavioral: 90.0
        resp_s1_t = InterviewResponse(
            session_id=session_a1.id,
            question_id=q_tech.id,
            answer_text="Ans 1",
            performance_score=80.0
        )
        resp_s1_ps = InterviewResponse(
            session_id=session_a1.id,
            question_id=q_ps.id,
            answer_text="Ans 2",
            performance_score=70.0
        )
        resp_s1_b = InterviewResponse(
            session_id=session_a1.id,
            question_id=q_beh.id,
            answer_text="Ans 3",
            performance_score=90.0
        )

        # Responses for Session 2:
        # Technical: 90.0
        resp_s2_t = InterviewResponse(
            session_id=session_a2.id,
            question_id=q_tech.id,
            answer_text="Ans 4",
            performance_score=90.0
        )
        db.add_all([resp_s1_t, resp_s1_ps, resp_s1_b, resp_s2_t])
        db.commit()

        # Math verification:
        # Tech scores: [80.0, 90.0] -> avg = 85.0
        # PS scores: [70.0] -> avg = 70.0
        # Beh scores: [90.0] -> avg = 90.0
        # Total scores: [80.0, 70.0, 90.0, 90.0] -> avg = 330 / 4 = 82.50

        res_a_interviews = client.get("/analytics/dashboard", headers=headers_a)
        assert res_a_interviews.status_code == 200
        data_a = res_a_interviews.json()

        assert data_a["interview_stats"]["total_sessions"] == 2
        assert data_a["interview_stats"]["completed_interviews"] == 1
        assert data_a["interview_stats"]["in_progress_interviews"] == 1
        assert data_a["interview_stats"]["total_responses"] == 4
        assert data_a["interview_stats"]["average_score"] == 82.50

        assert data_a["category_performance"]["technical_average"] == 85.0
        assert data_a["category_performance"]["problem_solving_average"] == 70.0
        assert data_a["category_performance"]["behavioral_average"] == 90.0

        # Recent interviews check
        assert len(data_a["recent_interviews"]) == 2
        s2_item = next(item for item in data_a["recent_interviews"] if item["id"] == session_a2.id)
        assert s2_item["status"] == "IN_PROGRESS"
        assert s2_item["current_difficulty"] == "HARD"
        assert s2_item["response_count"] == 1
        assert s2_item["average_score"] == 90.0

        s1_item = next(item for item in data_a["recent_interviews"] if item["id"] == session_a1.id)
        assert s1_item["status"] == "COMPLETED"
        assert s1_item["current_difficulty"] == "MEDIUM"
        assert s1_item["response_count"] == 3
        assert s1_item["average_score"] == round((80.0 + 70.0 + 90.0) / 3, 2)
        print("PASS: Multiple sessions and category scores aggregated with 100% mathematical accuracy.")

        # ----------------------------------------------------
        # 5. Multiple Career Readiness reports test
        # ----------------------------------------------------
        print("\n[TEST 5] Multiple Career Readiness reports & progression trends...")
        resume_a = Resume(
            user_id=user_a.id,
            original_filename="alice_resume.pdf",
            file_type="application/pdf",
            file_path="tmp/alice_resume.pdf",
            extracted_text="Python FastAPI Docker Kubernetes PostgreSQL",
            skills=["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL"]
        )
        db.add(resume_a)
        db.commit()
        created_resume_ids.append(resume_a.id)

        # Report 1 (Developing tier: 62.50)
        report_1 = CareerReadinessReport(
            user_id=user_a.id,
            interview_session_id=session_a1.id,
            resume_id=resume_a.id,
            target_job_role="Software Engineer",
            technical_score=60.0,
            problem_solving_score=60.0,
            communication_score=65.0,
            behavioral_score=65.0,
            resume_skill_match_score=60.0,
            interview_performance_score=60.0,
            overall_readiness_score=62.50,
            generated_at=now - timedelta(days=2)
        )
        # Report 2 (Strong tier: 88.00)
        report_2 = CareerReadinessReport(
            user_id=user_a.id,
            interview_session_id=session_a1.id,
            resume_id=resume_a.id,
            target_job_role="Software Engineer",
            technical_score=90.0,
            problem_solving_score=85.0,
            communication_score=85.0,
            behavioral_score=90.0,
            resume_skill_match_score=85.0,
            interview_performance_score=88.0,
            overall_readiness_score=88.00,
            generated_at=now
        )
        db.add_all([report_1, report_2])
        db.commit()
        created_report_ids.extend([report_1.id, report_2.id])

        res_reports = client.get("/analytics/dashboard", headers=headers_a)
        assert res_reports.status_code == 200
        data_a_rep = res_reports.json()

        # Latest report must be Report 2
        cr = data_a_rep["career_readiness"]
        assert cr["latest_report"] is not None
        assert cr["latest_report"]["id"] == report_2.id
        assert cr["latest_report"]["overall_readiness_score"] == 88.00
        assert cr["overall_readiness_score"] == 88.00
        assert cr["readiness_tier"] == "Strong"
        assert len(cr["latest_report"]["recommendations"]) > 0
        assert "technical" in cr["latest_report"]["component_recommendations"]

        # History must contain both reports in chronological order
        assert len(cr["history"]) == 2
        assert cr["history"][0]["id"] == report_1.id
        assert cr["history"][0]["overall_readiness_score"] == 62.50
        assert cr["history"][1]["id"] == report_2.id
        assert cr["history"][1]["overall_readiness_score"] == 88.00
        print("PASS: Career Readiness latest report, 4-tier categorization, and historical trends verified.")

        # ----------------------------------------------------
        # 6. Cross-user data isolation test
        # ----------------------------------------------------
        print("\n[TEST 6] Cross-user data isolation verification...")
        res_iso_b = client.get("/analytics/dashboard", headers=headers_b)
        assert res_iso_b.status_code == 200
        data_iso_b = res_iso_b.json()

        # User B must NOT see User A's interview sessions
        assert data_iso_b["interview_stats"]["total_sessions"] == 0
        assert data_iso_b["interview_stats"]["total_responses"] == 0
        assert data_iso_b["interview_stats"]["average_score"] is None
        assert data_iso_b["recent_interviews"] == []

        # User B must NOT see User A's readiness reports
        assert data_iso_b["career_readiness"]["latest_report"] is None
        assert data_iso_b["career_readiness"]["overall_readiness_score"] is None
        assert data_iso_b["career_readiness"]["history"] == []

        # User B only sees their own resume
        assert data_iso_b["resume_stats"]["resume_count"] == 1
        assert data_iso_b["resume_stats"]["latest_resume"]["original_filename"] == "bob_resume.pdf"
        assert data_iso_b["resume_stats"]["latest_resume"]["id"] == resume_b.id
        print("PASS: Cross-user data isolation strictly verified. Zero data leakage between accounts.")

        print("\n==================================================")
        print("ALL DASHBOARD & ANALYTICS API TESTS PASSED!")
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
    run_analytics_tests()
