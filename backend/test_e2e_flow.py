"""
HireMind Milestone 11: Unified End-to-End (E2E) Lifecycle Integration Test.

Executes the complete candidate workflow across Milestones 1 to 10 in a single unified run:
1. Candidate Registration (POST /auth/register)
2. Authentication & JWT Issuance (POST /auth/login)
3. Profile Verification & Update (GET /users/me, PUT /users/me)
4. Resume Upload & Skill Extraction (POST /resumes/upload)
5. Semantic ML Resume Analysis (POST /ml/analyze-resume)
6. Adaptive Interview Session Initialization (POST /interviews/start)
7. Dynamic Question Progression & Answer Evaluation:
   - Category 1: Technical Knowledge
   - Category 2: Problem Solving
   - Category 3: Behavioral Readiness
8. Career Readiness Report Generation & Verification (POST /career-readiness/generate)
9. Report Retrieval & Consistency Verification (GET /career-readiness/{id})
10. Real-time Dashboard Analytics Verification (GET /analytics/dashboard)
"""

import sys
import os
import uuid
import tempfile
from fpdf import FPDF
from fastapi.testclient import TestClient

# Add backend root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import app
from database.connection import SessionLocal
import models.user
from models.user import User
from models.resume import Resume
from models.interview import InterviewSession, InterviewQuestion, InterviewResponse
from models.readiness import CareerReadinessReport

client = TestClient(app)


def create_temp_pdf(content: str) -> str:
    """Generates a temporary valid PDF file on disk."""
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f"e2e_resume_{uuid.uuid4().hex[:8]}.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.multi_cell(0, 10, content)
    pdf.output(pdf_path)
    return pdf_path


def run_e2e_integration_flow():
    print("\n" + "=" * 65)
    print("RUNNING MILESTONE 11: COMPLETE END-TO-END WORKFLOW INTEGRATION TEST")
    print("=" * 65)

    db = SessionLocal()

    created_user_id = None
    created_resume_id = None
    created_session_id = None
    created_report_id = None
    temp_pdf_file = None

    try:
        # -------------------------------------------------------------
        # STEP 1: Candidate Registration
        # -------------------------------------------------------------
        print("\n[STEP 1] Registering candidate account...")
        user_uuid = uuid.uuid4().hex[:8]
        email = f"e2e_candidate_{user_uuid}@example.com"
        password = "SecurePassword123!"
        
        reg_payload = {
            "name": f"Alex Candidate {user_uuid}",
            "email": email,
            "password": password,
            "target_job_role": "Software Engineer"
        }
        res_reg = client.post("/auth/register", json=reg_payload)
        assert res_reg.status_code == 201, f"Registration failed: {res_reg.status_code} - {res_reg.text}"
        user_data = res_reg.json()
        created_user_id = user_data["id"]
        assert user_data["email"] == email
        print(f"  -> SUCCESS: Registered candidate ID {created_user_id} ({email})")

        # -------------------------------------------------------------
        # STEP 2: Authentication & Token Issuance
        # -------------------------------------------------------------
        print("\n[STEP 2] Authenticating candidate...")
        login_payload = {"email": email, "password": password}
        res_login = client.post("/auth/login", json=login_payload)
        assert res_login.status_code == 200, f"Login failed: {res_login.status_code} - {res_login.text}"
        token_data = res_login.json()
        assert "access_token" in token_data
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print("  -> SUCCESS: Obtained JWT access token.")

        # -------------------------------------------------------------
        # STEP 3: Profile Verification & Role Alignment
        # -------------------------------------------------------------
        print("\n[STEP 3] Verifying and updating candidate profile...")
        res_profile = client.get("/users/me", headers=headers)
        assert res_profile.status_code == 200
        assert res_profile.json()["id"] == created_user_id

        res_update = client.put(
            "/users/me",
            headers=headers,
            json={"name": f"Alex Developer {user_uuid}", "target_job_role": "Software Engineer"}
        )
        assert res_update.status_code == 200
        assert res_update.json()["name"] == f"Alex Developer {user_uuid}"
        print("  -> SUCCESS: Candidate profile verified and updated.")

        # -------------------------------------------------------------
        # STEP 4: Resume Upload & Skill Extraction
        # -------------------------------------------------------------
        print("\n[STEP 4] Uploading PDF resume and performing skill extraction...")
        resume_text = (
            "Alex Developer - Full Stack Software Engineer. "
            "Skilled in Python, React, SQL, FastAPI, Docker, and AWS. "
            "Developed high-throughput microservices using PostgreSQL and automated CI/CD pipelines. "
            "Strong foundation in data structures, algorithms, and system design."
        )
        temp_pdf_file = create_temp_pdf(resume_text)

        with open(temp_pdf_file, "rb") as f:
            res_upload = client.post(
                "/resumes/upload",
                headers=headers,
                files={"file": ("alex_developer_resume.pdf", f, "application/pdf")}
            )
        assert res_upload.status_code == 201, f"Resume upload failed: {res_upload.status_code} - {res_upload.text}"
        resume_data = res_upload.json()
        created_resume_id = resume_data["id"]
        extracted_skills = resume_data.get("skills", [])
        assert "Python" in extracted_skills, f"Expected 'Python' in skills, got: {extracted_skills}"
        assert "React" in extracted_skills, f"Expected 'React' in skills, got: {extracted_skills}"
        assert "SQL" in extracted_skills, f"Expected 'SQL' in skills, got: {extracted_skills}"
        print(f"  -> SUCCESS: Resume ID {created_resume_id} processed. Skills: {extracted_skills}")

        # -------------------------------------------------------------
        # STEP 5: Semantic ML Resume Analysis
        # -------------------------------------------------------------
        print("\n[STEP 5] Running semantic ML analysis against 'Software Engineer' role...")
        ml_payload = {"resume_id": created_resume_id, "target_job_role": "Software Engineer"}
        res_ml = client.post("/ml/analyze-resume", headers=headers, json=ml_payload)
        assert res_ml.status_code == 200, f"ML analysis failed: {res_ml.status_code} - {res_ml.text}"
        ml_data = res_ml.json()
        semantic_sim = ml_data["semantic_similarity"]
        assert 0.0 <= semantic_sim <= 1.0, f"Invalid semantic similarity: {semantic_sim}"
        assert ml_data["embedding_dimension"] == 384
        print(f"  -> SUCCESS: ML Semantic Similarity: {semantic_sim:.4f} (Embedding Dim: 384)")

        # -------------------------------------------------------------
        # STEP 6: Adaptive Interview Session Start
        # -------------------------------------------------------------
        print("\n[STEP 6] Starting adaptive interview for 'Software Engineer'...")
        start_payload = {"target_job_role": "Software Engineer"}
        res_start = client.post("/interviews/start", headers=headers, json=start_payload)
        assert res_start.status_code == 200, f"Interview start failed: {res_start.status_code} - {res_start.text}"
        session_data = res_start.json()
        created_session_id = session_data["id"]
        assert session_data["status"] == "IN_PROGRESS"
        assert session_data["current_question"] is not None
        print(f"  -> SUCCESS: Interview session {created_session_id} started.")

        # -------------------------------------------------------------
        # STEP 7: Answering 3 Adaptive Interview Questions
        # -------------------------------------------------------------
        print("\n[STEP 7] Answering interview questions across 3 core categories...")
        current_session = session_data
        question_count = 0

        while current_session["status"] == "IN_PROGRESS" and current_session.get("current_question"):
            question_count += 1
            q = current_session["current_question"]
            q_id = q["id"]
            category = q["category"]
            difficulty = q["difficulty"]
            print(f"  Question {question_count} [{category} - {difficulty}]: {q['question_text'][:70]}...")

            # Provide high-quality domain responses
            if category == "Technical":
                answer_text = (
                    "To optimize SQL queries, I create appropriate B-tree indexes on WHERE and JOIN predicates, "
                    "analyze EXPLAIN ANALYZE execution plans to eliminate sequential scans, avoid SELECT * in production, "
                    "and implement connection pooling to minimize connection overhead."
                )
            elif category == "Problem Solving":
                answer_text = (
                    "I approach system bottlenecks by identifying resource metrics such as CPU saturation, disk I/O, "
                    "and memory leaks using APM profiling tools. I then implement caching using Redis, optimize database "
                    "indexing, and distribute workloads across worker queues."
                )
            else:  # Behavioral
                answer_text = (
                    "In my previous project, we faced a major architectural dispute regarding microservices vs monolith. "
                    "I scheduled a design review meeting, documented the trade-offs of both approaches with benchmark data, "
                    "and aligned the team on a phased modular monolith approach that shipped on schedule."
                )

            answer_payload = {"question_id": q_id, "answer_text": answer_text}
            res_ans = client.post(
                f"/interviews/{created_session_id}/answer",
                headers=headers,
                json=answer_payload
            )
            assert res_ans.status_code == 200, f"Answer failed: {res_ans.status_code} - {res_ans.text}"
            current_session = res_ans.json()
            latest_eval = current_session.get("latest_evaluation", {})
            print(f"    -> Score: {latest_eval.get('performance_score')} | Semantic Sim: {latest_eval.get('semantic_similarity'):.3f}")

        assert current_session["status"] == "COMPLETED", "Expected session to reach COMPLETED status."
        print(f"  -> SUCCESS: Completed interview with {question_count} responses answered.")

        # -------------------------------------------------------------
        # STEP 8: Career Readiness Report Generation
        # -------------------------------------------------------------
        print("\n[STEP 8] Generating Career Readiness Report...")
        report_payload = {
            "interview_session_id": created_session_id,
            "resume_id": created_resume_id
        }
        res_rep = client.post("/career-readiness/generate", headers=headers, json=report_payload)
        assert res_rep.status_code == 200, f"Report generation failed: {res_rep.status_code} - {res_rep.text}"
        report_data = res_rep.json()
        created_report_id = report_data["id"]

        overall_score = report_data["overall_readiness_score"]
        assert 0.0 <= overall_score <= 100.0
        assert report_data["technical_score"] > 0
        assert report_data["problem_solving_score"] > 0
        assert report_data["communication_score"] > 0
        assert report_data["behavioral_score"] > 0
        assert report_data["resume_skill_match_score"] > 0
        assert report_data["interview_performance_score"] > 0
        assert len(report_data["recommendations"]) > 0
        assert "technical" in report_data["component_recommendations"]

        print(f"  -> SUCCESS: Career Readiness Report #{created_report_id} generated.")
        print(f"     Overall Readiness: {overall_score:.1f}%")
        print(f"     Technical: {report_data['technical_score']:.1f}% | Problem Solving: {report_data['problem_solving_score']:.1f}% | Behavioral: {report_data['behavioral_score']:.1f}%")
        print(f"     Communication: {report_data['communication_score']:.1f}% | Resume Skill Match: {report_data['resume_skill_match_score']:.1f}%")

        # -------------------------------------------------------------
        # STEP 9: Report Retrieval Verification
        # -------------------------------------------------------------
        print("\n[STEP 9] Verifying report retrieval by ID...")
        res_get_rep = client.get(f"/career-readiness/{created_report_id}", headers=headers)
        assert res_get_rep.status_code == 200
        retrieved_report = res_get_rep.json()
        assert retrieved_report["id"] == created_report_id
        assert retrieved_report["overall_readiness_score"] == overall_score
        print("  -> SUCCESS: Career Readiness Report retrieval matches persisted data.")

        # -------------------------------------------------------------
        # STEP 10: Dashboard Analytics Verification
        # -------------------------------------------------------------
        print("\n[STEP 10] Fetching Dashboard Analytics (GET /analytics/dashboard)...")
        res_dash = client.get("/analytics/dashboard", headers=headers)
        assert res_dash.status_code == 200, f"Dashboard fetch failed: {res_dash.status_code} - {res_dash.text}"
        dash = res_dash.json()

        # Check Interview Statistics
        int_stats = dash["interview_stats"]
        assert int_stats["total_sessions"] >= 1
        assert int_stats["completed_interviews"] >= 1
        assert int_stats["total_responses"] >= 3
        assert int_stats["average_score"] is not None and int_stats["average_score"] > 0

        # Check Category Breakdown
        cat_perf = dash["category_performance"]
        assert cat_perf["technical_average"] is not None and cat_perf["technical_average"] > 0
        assert cat_perf["problem_solving_average"] is not None and cat_perf["problem_solving_average"] > 0
        assert cat_perf["behavioral_average"] is not None and cat_perf["behavioral_average"] > 0

        # Check Resume Statistics
        res_stats = dash["resume_stats"]
        assert res_stats["resume_count"] >= 1
        assert res_stats["latest_resume"]["id"] == created_resume_id
        assert len(res_stats["extracted_skills"]) >= 3

        # Check Career Readiness
        cr_stats = dash["career_readiness"]
        assert cr_stats["latest_report"] is not None
        assert cr_stats["overall_readiness_score"] == overall_score
        assert cr_stats["latest_report"]["technical_score"] == report_data["technical_score"]
        assert cr_stats["latest_report"]["problem_solving_score"] == report_data["problem_solving_score"]
        assert len(cr_stats["history"]) >= 1

        print("  -> SUCCESS: All Dashboard Analytics cards, breakdown metrics, and history verified.")

        print("\n" + "=" * 65)
        print("ALL END-TO-END WORKFLOW INTEGRATION STEPS PASSED (10/10)")
        print("=" * 65)

    finally:
        # Clean up temporary test file
        if temp_pdf_file and os.path.exists(temp_pdf_file):
            try:
                os.remove(temp_pdf_file)
            except Exception:
                pass

        # Clean up database records
        if created_report_id:
            db.query(CareerReadinessReport).filter(CareerReadinessReport.id == created_report_id).delete()
        if created_session_id:
            db.query(InterviewResponse).filter(InterviewResponse.session_id == created_session_id).delete()
            db.query(InterviewSession).filter(InterviewSession.id == created_session_id).delete()
        if created_resume_id:
            db.query(Resume).filter(Resume.id == created_resume_id).delete()
        if created_user_id:
            db.query(User).filter(User.id == created_user_id).delete()
        db.commit()
        db.close()


if __name__ == "__main__":
    run_e2e_integration_flow()
