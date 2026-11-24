"""
Comprehensive Unit and Integration Tests for HireMind Milestone 9: Career Readiness Analyzer.

Covers:
1. Pure mathematical helper formulas (all 6 dimensions + overall + recommendations + _compute_component empty check)
2. Four recommendation thresholds (Below 50, 50-69, 70-84, 85-100)
3. Target job role validation using profile infrastructure
4. Required AI evaluation fields validation (performance_score, semantic_similarity, concept_coverage, completeness_score)
5. Missing data validation (incomplete session, missing responses, missing category, missing resume text)
6. Ownership validation (session or resume belonging to another user)
7. Persistence verification (persisting report to DB and reloading)
8. Database rollback handling on persistence failure
9. MiniLM embedding encoder reuse (real get_model() integration)
"""

import sys
import os
import uuid
from unittest.mock import MagicMock

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.career_readiness import (
    _compute_component,
    calculate_technical_score,
    calculate_problem_solving_score,
    calculate_behavioral_score,
    calculate_communication_score,
    calculate_interview_performance,
    calculate_overall_readiness,
    calculate_resume_match,
    generate_recommendations,
    get_component_recommendations,
    generate_report
)
from models.user import User
from models.resume import Resume
from models.interview import InterviewSession, InterviewQuestion, InterviewResponse
from models.readiness import CareerReadinessReport
from database.connection import SessionLocal


def test_math_formulas():
    """Test pure math helper functions without touching database."""
    print("Testing pure math helpers...")
    
    # Empty list check for _compute_component
    try:
        _compute_component([])
        assert False, "Should raise ValueError for empty score list"
    except ValueError as e:
        assert "Cannot compute score for an empty list" in str(e)
    
    # 1. Technical Knowledge (average of Technical responses)
    responses = [
        {"category": "Technical", "performance_score": 80.0},
        {"category": "Technical", "performance_score": 90.0},
        {"category": "Behavioral", "performance_score": 40.0}
    ]
    assert calculate_technical_score(responses) == 85.0
    
    # 2. Problem Solving (average of Problem Solving responses)
    responses = [
        {"category": "Problem Solving", "performance_score": 70.0},
        {"category": "Technical", "performance_score": 90.0}
    ]
    assert calculate_problem_solving_score(responses) == 70.0
    
    # 3. Behavioral Readiness (average of Behavioral responses)
    responses = [
        {"category": "Behavioral", "performance_score": 60.0},
        {"category": "Behavioral", "performance_score": 100.0}
    ]
    assert calculate_behavioral_score(responses) == 80.0
    
    # 4. Communication / Answer Quality (60% avg semantic_similarity + 40% avg completeness_score)
    responses = [
        {"semantic_similarity": 50.0, "completeness_score": 100.0},
        {"semantic_similarity": 100.0, "completeness_score": 50.0}
    ]
    assert calculate_communication_score(responses) == 75.0
    
    responses2 = [
        {"semantic_similarity": 80.0, "completeness_score": 90.0}
    ]
    assert calculate_communication_score(responses2) == 84.0
    
    # 5. Interview Performance (average across all questions)
    responses = [
        {"category": "Technical", "performance_score": 50.0},
        {"category": "Problem Solving", "performance_score": 100.0}
    ]
    assert calculate_interview_performance(responses) == 75.0
    
    # 6. Overall Readiness aggregation
    # Tech(25%), PS(20%), Comm(20%), Behav(15%), Resume(10%), Perf(10%)
    assert calculate_overall_readiness(100, 100, 100, 100, 100, 100) == 100.0
    assert calculate_overall_readiness(80, 80, 80, 80, 80, 80) == 80.0
    
    custom_score = calculate_overall_readiness(80.0, 70.0, 80.0, 90.0, 85.0, 80.0)
    assert custom_score == 80.0
    
    # 7. Recommendations generation across 4 thresholds
    recs = generate_recommendations(40.0, 65.0, 40.0, 80.0, 40.0, 90.0)
    assert len(recs) == 4
    assert any("technical" in r.lower() for r in recs)
    assert any("problem-solving" in r.lower() for r in recs)
    
    # Solid readiness (between 70 and 84)
    solid_recs = generate_recommendations(75.0, 78.0, 80.0, 72.0, 84.0, 76.0)
    assert len(solid_recs) == 1
    assert "solid readiness" in solid_recs[0].lower()
    
    # Strong readiness (>= 85)
    strong_recs = generate_recommendations(85.0, 85.0, 85.0, 85.0, 85.0, 85.0)
    assert len(strong_recs) == 1
    assert "strong readiness" in strong_recs[0].lower()
    
    # Component recommendations across all four tiers
    comp_recs = get_component_recommendations(40.0, 60.0, 75.0, 90.0, 45.0, 70.0)
    assert "Needs substantial improvement" in comp_recs["technical"]
    assert "Developing" in comp_recs["problem_solving"]
    assert "Solid" in comp_recs["communication"]
    assert "Strong" in comp_recs["behavioral"]
    assert "Needs substantial improvement" in comp_recs["resume_skill_match"]
    assert "Solid" in comp_recs["interview_performance"]
    
    print("Math tests passed.")


def test_missing_data_and_validation():
    """Test validation of missing data, incomplete interviews, missing evaluation fields, and role profiles."""
    print("Testing missing data and category enforcement...")
    db = SessionLocal()
    
    created_user_ids = []
    created_session_ids = []
    created_resume_ids = []
    created_q_ids = []
    
    try:
        user = User(name="TestM9User", email=f"test_m9_{uuid.uuid4()}@example.com", password_hash="hash")
        db.add(user)
        db.commit()
        created_user_ids.append(user.id)
        
        # 1. Non-existent session
        try:
            generate_report(db, user.id, 999999, 999999)
            assert False, "Should raise exception for non-existent session"
        except ValueError as e:
            assert "Interview session not found" in str(e)
            
        # 2. Incomplete interview session (status = IN_PROGRESS)
        session = InterviewSession(user_id=user.id, target_job_role="Software Engineer", status="IN_PROGRESS")
        resume = Resume(
            user_id=user.id,
            extracted_text="Python FastAPI SQL",
            original_filename="res.pdf",
            file_type="pdf",
            file_path="tmp/res.pdf"
        )
        db.add_all([session, resume])
        db.commit()
        created_session_ids.append(session.id)
        created_resume_ids.append(resume.id)
        
        try:
            generate_report(db, user.id, session.id, resume.id)
            assert False, "Should raise exception for incomplete interview"
        except ValueError as e:
            assert "incomplete interview" in str(e)
            
        # Mark completed
        session.status = "COMPLETED"
        db.commit()
        
        # 3. Resume with empty text
        empty_resume = Resume(
            user_id=user.id,
            extracted_text="   ",
            original_filename="empty.pdf",
            file_type="pdf",
            file_path="tmp/empty.pdf"
        )
        db.add(empty_resume)
        db.commit()
        created_resume_ids.append(empty_resume.id)
        
        try:
            generate_report(db, user.id, session.id, empty_resume.id)
            assert False, "Should raise exception for empty resume text"
        except ValueError as e:
            assert "Resume text is missing or unreadable" in str(e)
            
        # 4. Invalid target job role validation
        invalid_role_session = InterviewSession(user_id=user.id, target_job_role="Unsupported Role 123", status="COMPLETED")
        db.add(invalid_role_session)
        db.commit()
        created_session_ids.append(invalid_role_session.id)
        
        try:
            generate_report(db, user.id, invalid_role_session.id, resume.id)
            assert False, "Should raise exception for unsupported target role"
        except ValueError as e:
            assert "Invalid target job role" in str(e) or "not currently supported" in str(e)
            
        # 5. Completed session with no responses
        try:
            generate_report(db, user.id, session.id, resume.id)
            assert False, "Should raise exception for no responses"
        except ValueError as e:
            assert "No interview responses found" in str(e)
            
        # 6. Add questions and partial responses (missing Problem Solving & Behavioral)
        q_tech = InterviewQuestion(
            target_job_role="Software Engineer", category="Technical",
            question_text="Tech Q", difficulty="MEDIUM"
        )
        q_ps = InterviewQuestion(
            target_job_role="Software Engineer", category="Problem Solving",
            question_text="PS Q", difficulty="MEDIUM"
        )
        q_beh = InterviewQuestion(
            target_job_role="Software Engineer", category="Behavioral",
            question_text="Beh Q", difficulty="MEDIUM"
        )
        db.add_all([q_tech, q_ps, q_beh])
        db.commit()
        created_q_ids.extend([q_tech.id, q_ps.id, q_beh.id])
        
        r_tech = InterviewResponse(
            session_id=session.id, question_id=q_tech.id, answer_text="Tech answer",
            performance_score=80.0, semantic_similarity=80.0, concept_coverage=80.0, completeness_score=80.0
        )
        db.add(r_tech)
        db.commit()
        
        # Missing Problem Solving
        try:
            generate_report(db, user.id, session.id, resume.id)
            assert False, "Should raise exception for missing Problem Solving"
        except ValueError as e:
            assert "Missing Problem Solving responses" in str(e)
            
        # Add Problem Solving, missing Behavioral
        r_ps = InterviewResponse(
            session_id=session.id, question_id=q_ps.id, answer_text="PS answer",
            performance_score=75.0, semantic_similarity=75.0, concept_coverage=75.0, completeness_score=75.0
        )
        db.add(r_ps)
        db.commit()
        
        try:
            generate_report(db, user.id, session.id, resume.id)
            assert False, "Should raise exception for missing Behavioral"
        except ValueError as e:
            assert "Missing Behavioral responses" in str(e)
            
        # 7. Response missing concept_coverage
        r_beh_missing_concept = InterviewResponse(
            session_id=session.id, question_id=q_beh.id, answer_text="Beh answer",
            performance_score=70.0, semantic_similarity=70.0, concept_coverage=None, completeness_score=70.0
        )
        db.add(r_beh_missing_concept)
        db.commit()
        
        try:
            generate_report(db, user.id, session.id, resume.id)
            assert False, "Should raise exception when concept_coverage is None"
        except ValueError as e:
            assert "Required AI evaluation data is missing" in str(e)
            
        # Clean up that response
        db.delete(r_beh_missing_concept)
        db.commit()
        
        # 8. Response missing completeness_score
        r_beh_missing_comp = InterviewResponse(
            session_id=session.id, question_id=q_beh.id, answer_text="Beh answer",
            performance_score=70.0, semantic_similarity=70.0, concept_coverage=70.0, completeness_score=None
        )
        db.add(r_beh_missing_comp)
        db.commit()
        
        try:
            generate_report(db, user.id, session.id, resume.id)
            assert False, "Should raise exception when completeness_score is None"
        except ValueError as e:
            assert "Required AI evaluation data is missing" in str(e)
            
        print("Missing data and validation tests passed.")
        
    finally:
        db.rollback()
        for sid in created_session_ids:
            db.execute(CareerReadinessReport.__table__.delete().where(CareerReadinessReport.interview_session_id == sid))
            db.execute(InterviewResponse.__table__.delete().where(InterviewResponse.session_id == sid))
            db.execute(InterviewSession.__table__.delete().where(InterviewSession.id == sid))
        if created_q_ids:
            db.execute(InterviewQuestion.__table__.delete().where(InterviewQuestion.id.in_(created_q_ids)))
        for rid in created_resume_ids:
            db.execute(Resume.__table__.delete().where(Resume.id == rid))
        for uid in created_user_ids:
            db.execute(User.__table__.delete().where(User.id == uid))
        db.commit()
        db.close()


def test_ownership_validation():
    """Test that users cannot access sessions or resumes belonging to another user."""
    print("Testing ownership validation...")
    db = SessionLocal()
    created_user_ids = []
    created_session_ids = []
    created_resume_ids = []
    
    try:
        user_a = User(name="UserA", email=f"user_a_{uuid.uuid4()}@example.com", password_hash="hash")
        user_b = User(name="UserB", email=f"user_b_{uuid.uuid4()}@example.com", password_hash="hash")
        db.add_all([user_a, user_b])
        db.commit()
        created_user_ids.extend([user_a.id, user_b.id])
        
        session_b = InterviewSession(user_id=user_b.id, target_job_role="Software Engineer", status="COMPLETED")
        resume_a = Resume(user_id=user_a.id, extracted_text="Resume A", original_filename="a.pdf", file_type="pdf", file_path="tmp/a.pdf")
        resume_b = Resume(user_id=user_b.id, extracted_text="Resume B", original_filename="b.pdf", file_type="pdf", file_path="tmp/b.pdf")
        db.add_all([session_b, resume_a, resume_b])
        db.commit()
        created_session_ids.append(session_b.id)
        created_resume_ids.extend([resume_a.id, resume_b.id])
        
        # User A trying to access User B's session
        try:
            generate_report(db, user_a.id, session_b.id, resume_a.id)
            assert False, "Should reject cross-user interview session access"
        except ValueError as e:
            assert "Not authorized to access this interview session" in str(e)
            
        # User B trying to access User A's resume
        try:
            generate_report(db, user_b.id, session_b.id, resume_a.id)
            assert False, "Should reject cross-user resume access"
        except ValueError as e:
            assert "Not authorized to access this resume" in str(e)
            
        print("Ownership tests passed.")
        
    finally:
        db.rollback()
        for sid in created_session_ids:
            db.execute(InterviewSession.__table__.delete().where(InterviewSession.id == sid))
        for rid in created_resume_ids:
            db.execute(Resume.__table__.delete().where(Resume.id == rid))
        for uid in created_user_ids:
            db.execute(User.__table__.delete().where(User.id == uid))
        db.commit()
        db.close()


def test_persistence_and_database():
    """Test successful report generation, persistence, and DB querying."""
    print("Testing report persistence in database...")
    db = SessionLocal()
    created_user_ids = []
    created_session_ids = []
    created_resume_ids = []
    created_q_ids = []
    created_report_ids = []
    
    try:
        user = User(name="PersistUser", email=f"persist_{uuid.uuid4()}@example.com", password_hash="hash")
        db.add(user)
        db.commit()
        created_user_ids.append(user.id)
        
        session = InterviewSession(user_id=user.id, target_job_role="Software Engineer", status="COMPLETED")
        resume = Resume(
            user_id=user.id,
            extracted_text="Software engineer with Python and Docker experience",
            original_filename="res.pdf",
            file_type="pdf",
            file_path="tmp/res.pdf"
        )
        db.add_all([session, resume])
        db.commit()
        created_session_ids.append(session.id)
        created_resume_ids.append(resume.id)
        
        q_tech = InterviewQuestion(target_job_role="Software Engineer", category="Technical", question_text="Tech Q", difficulty="MEDIUM")
        q_ps = InterviewQuestion(target_job_role="Software Engineer", category="Problem Solving", question_text="PS Q", difficulty="MEDIUM")
        q_beh = InterviewQuestion(target_job_role="Software Engineer", category="Behavioral", question_text="Beh Q", difficulty="MEDIUM")
        db.add_all([q_tech, q_ps, q_beh])
        db.commit()
        created_q_ids.extend([q_tech.id, q_ps.id, q_beh.id])
        
        r_tech = InterviewResponse(session_id=session.id, question_id=q_tech.id, answer_text="Ans 1", performance_score=80.0, semantic_similarity=80.0, concept_coverage=80.0, completeness_score=80.0)
        r_ps = InterviewResponse(session_id=session.id, question_id=q_ps.id, answer_text="Ans 2", performance_score=70.0, semantic_similarity=70.0, concept_coverage=70.0, completeness_score=70.0)
        r_beh = InterviewResponse(session_id=session.id, question_id=q_beh.id, answer_text="Ans 3", performance_score=90.0, semantic_similarity=90.0, concept_coverage=90.0, completeness_score=90.0)
        db.add_all([r_tech, r_ps, r_beh])
        db.commit()
        
        # Mock resume match for controlled math verification
        import services.career_readiness
        original_match = services.career_readiness.calculate_resume_match
        services.career_readiness.calculate_resume_match = lambda text, role: 85.0
        
        try:
            report = generate_report(db, user.id, session.id, resume.id)
            created_report_ids.append(report.id)
            
            assert report.id is not None
            assert report.target_job_role == "Software Engineer"
            assert report.technical_score == 80.0
            assert report.problem_solving_score == 70.0
            assert report.communication_score == 80.0
            assert report.behavioral_score == 90.0
            assert report.resume_skill_match_score == 85.0
            assert report.interview_performance_score == 80.0
            assert report.overall_readiness_score == 80.0
            assert report.generated_at is not None
            
            # Query back from DB
            db_report = db.query(CareerReadinessReport).filter(CareerReadinessReport.id == report.id).first()
            assert db_report is not None
            assert db_report.overall_readiness_score == 80.0
            print("Persistence test passed.")
        finally:
            services.career_readiness.calculate_resume_match = original_match
            
    finally:
        db.rollback()
        for rep_id in created_report_ids:
            db.execute(CareerReadinessReport.__table__.delete().where(CareerReadinessReport.id == rep_id))
        for sid in created_session_ids:
            db.execute(InterviewResponse.__table__.delete().where(InterviewResponse.session_id == sid))
            db.execute(InterviewSession.__table__.delete().where(InterviewSession.id == sid))
        if created_q_ids:
            db.execute(InterviewQuestion.__table__.delete().where(InterviewQuestion.id.in_(created_q_ids)))
        for rid in created_resume_ids:
            db.execute(Resume.__table__.delete().where(Resume.id == rid))
        for uid in created_user_ids:
            db.execute(User.__table__.delete().where(User.id == uid))
        db.commit()
        db.close()


def test_rollback_on_persistence_error():
    """Test that database rollback occurs cleanly if persistence fails."""
    print("Testing rollback on persistence failure...")
    db = SessionLocal()
    created_user_ids = []
    created_session_ids = []
    created_resume_ids = []
    created_q_ids = []
    
    try:
        user = User(name="RollbackUser", email=f"rollback_{uuid.uuid4()}@example.com", password_hash="hash")
        db.add(user)
        db.commit()
        created_user_ids.append(user.id)
        
        session = InterviewSession(user_id=user.id, target_job_role="Software Engineer", status="COMPLETED")
        resume = Resume(user_id=user.id, extracted_text="Some text", original_filename="res.pdf", file_type="pdf", file_path="tmp/res.pdf")
        db.add_all([session, resume])
        db.commit()
        created_session_ids.append(session.id)
        created_resume_ids.append(resume.id)
        
        q_tech = InterviewQuestion(target_job_role="Software Engineer", category="Technical", question_text="Tech Q", difficulty="MEDIUM")
        q_ps = InterviewQuestion(target_job_role="Software Engineer", category="Problem Solving", question_text="PS Q", difficulty="MEDIUM")
        q_beh = InterviewQuestion(target_job_role="Software Engineer", category="Behavioral", question_text="Beh Q", difficulty="MEDIUM")
        db.add_all([q_tech, q_ps, q_beh])
        db.commit()
        created_q_ids.extend([q_tech.id, q_ps.id, q_beh.id])
        
        r_tech = InterviewResponse(session_id=session.id, question_id=q_tech.id, answer_text="A1", performance_score=80.0, semantic_similarity=80.0, concept_coverage=80.0, completeness_score=80.0)
        r_ps = InterviewResponse(session_id=session.id, question_id=q_ps.id, answer_text="A2", performance_score=70.0, semantic_similarity=70.0, concept_coverage=70.0, completeness_score=70.0)
        r_beh = InterviewResponse(session_id=session.id, question_id=q_beh.id, answer_text="A3", performance_score=90.0, semantic_similarity=90.0, concept_coverage=90.0, completeness_score=90.0)
        db.add_all([r_tech, r_ps, r_beh])
        db.commit()
        
        import services.career_readiness
        original_match = services.career_readiness.calculate_resume_match
        services.career_readiness.calculate_resume_match = lambda text, role: 85.0
        
        # Monkeypatch db.commit to simulate database failure during save
        def failing_commit():
            raise Exception("Simulated DB connection failure")
            
        real_commit = db.commit
        db.commit = failing_commit
        
        try:
            generate_report(db, user.id, session.id, resume.id)
            assert False, "Should raise RuntimeError when persistence fails"
        except RuntimeError as e:
            assert "Database persistence failed" in str(e)
            print("Rollback test passed.")
        finally:
            db.commit = real_commit
            services.career_readiness.calculate_resume_match = original_match
            
    finally:
        db.rollback()
        for sid in created_session_ids:
            db.execute(InterviewResponse.__table__.delete().where(InterviewResponse.session_id == sid))
            db.execute(InterviewSession.__table__.delete().where(InterviewSession.id == sid))
        if created_q_ids:
            db.execute(InterviewQuestion.__table__.delete().where(InterviewQuestion.id.in_(created_q_ids)))
        for rid in created_resume_ids:
            db.execute(Resume.__table__.delete().where(Resume.id == rid))
        for uid in created_user_ids:
            db.execute(User.__table__.delete().where(User.id == uid))
        db.commit()
        db.close()


def test_minilm_integration():
    """Test direct calculate_resume_match with real get_model() MiniLM encoder."""
    print("Testing real MiniLM model integration for resume match...")
    resume_text = (
        "Experienced software engineer proficient in Python, FastAPI, and PostgreSQL. "
        "Built microservices and scalable REST APIs using Docker and Git."
    )
    score = calculate_resume_match(resume_text, "Software Engineer")
    print(f"Calculated MiniLM resume match score: {score}")
    assert isinstance(score, float)
    assert 0.0 <= score <= 100.0
    assert score > 40.0
    print("Real MiniLM integration test passed.")


if __name__ == "__main__":
    test_math_formulas()
    test_missing_data_and_validation()
    test_ownership_validation()
    test_persistence_and_database()
    test_rollback_on_persistence_error()
    test_minilm_integration()
    print("\n==================================================")
    print("ALL CAREER READINESS TESTS PASSED SUCCESSFULLY!")
    print("==================================================")
