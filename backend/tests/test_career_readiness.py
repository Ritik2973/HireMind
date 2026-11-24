import pytest
from unittest.mock import patch, MagicMock
from services.career_readiness import (
    calculate_technical_score,
    calculate_problem_solving_score,
    calculate_behavioral_score,
    calculate_communication_score,
    calculate_interview_performance,
    calculate_overall_readiness,
    generate_recommendations,
    generate_report
)
from models.readiness import CareerReadinessReport
from models.interview import InterviewSession, InterviewResponse, InterviewQuestion
from models.resume import Resume
from sqlalchemy.orm import Session

# --- 1. Math / Pure Logic Tests ---

def test_technical_score():
    responses = [
        {"category": "Technical", "performance_score": 80.0},
        {"category": "Technical", "performance_score": 90.0},
        {"category": "Behavioral", "performance_score": 40.0}
    ]
    assert calculate_technical_score(responses) == 85.0

def test_problem_solving_score():
    responses = [
        {"category": "Problem Solving", "performance_score": 70.0},
        {"category": "Technical", "performance_score": 90.0}
    ]
    assert calculate_problem_solving_score(responses) == 70.0

def test_behavioral_score():
    responses = [
        {"category": "Behavioral", "performance_score": 60.0},
        {"category": "Behavioral", "performance_score": 100.0}
    ]
    assert calculate_behavioral_score(responses) == 80.0

def test_communication_score():
    # 60% semantic + 40% completeness
    responses = [
        {"semantic_similarity": 50.0, "completeness_score": 100.0}, # (0.6*50 + 0.4*100) = 30 + 40 = 70
        {"semantic_similarity": 100.0, "completeness_score": 50.0}  # (0.6*100 + 0.4*50) = 60 + 20 = 80
    ]
    # Average of 70 and 80 = 75.0
    assert calculate_communication_score(responses) == 75.0

def test_interview_performance_score():
    responses = [
        {"category": "Technical", "performance_score": 50.0},
        {"category": "Problem Solving", "performance_score": 100.0}
    ]
    assert calculate_interview_performance(responses) == 75.0

def test_overall_readiness_score():
    # Weights: Tech (25%), PS (20%), Comm (20%), Behav (15%), Resume (10%), Perf (10%)
    tech = 100.0   # 25
    ps = 100.0     # 20
    comm = 100.0   # 20
    behav = 100.0  # 15
    resume = 100.0 # 10
    perf = 100.0   # 10
    assert calculate_overall_readiness(tech, ps, comm, behav, resume, perf) == 100.0
    
    # Another test
    assert calculate_overall_readiness(80, 80, 80, 80, 80, 80) == 80.0

def test_recommendations():
    recs = generate_recommendations(40.0, 60.0, 40.0, 80.0, 40.0, 90.0)
    assert len(recs) == 3
    assert any("Technical" in r or "technical" in r for r in recs)
    assert any("explaining ideas clearly" in r for r in recs)
    assert any("Strengthen skills and resume content" in r for r in recs)
    
    # All strong
    recs_good = generate_recommendations(90.0, 90.0, 90.0, 90.0, 90.0, 90.0)
    assert len(recs_good) == 1
    assert "strong readiness" in recs_good[0]


# --- 2. Database / Service Logic Tests ---

@patch('services.career_readiness.calculate_resume_match')
def test_generate_report_valid(mock_resume_match, db_session):
    mock_resume_match.return_value = 85.0
    
    # Create test data
    from models.user import User
    user = User(name="Test", email="test_readiness@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    resume = Resume(user_id=user.id, extracted_text="Some python java skills")
    db_session.add(resume)
    
    session = InterviewSession(user_id=user.id, target_job_role="Software Engineer", status="COMPLETED")
    db_session.add(session)
    db_session.commit()
    
    q_tech = InterviewQuestion(target_job_role="Software Engineer", category="Technical", question_text="Q1", expected_answer="A1", key_concepts=[], rubric_criteria=[])
    q_ps = InterviewQuestion(target_job_role="Software Engineer", category="Problem Solving", question_text="Q2", expected_answer="A2", key_concepts=[], rubric_criteria=[])
    q_beh = InterviewQuestion(target_job_role="Software Engineer", category="Behavioral", question_text="Q3", expected_answer="A3", key_concepts=[], rubric_criteria=[])
    db_session.add_all([q_tech, q_ps, q_beh])
    db_session.commit()
    
    r_tech = InterviewResponse(session_id=session.id, question_id=q_tech.id, answer_text="Ans", performance_score=80.0, semantic_similarity=80.0, completeness_score=80.0)
    r_ps = InterviewResponse(session_id=session.id, question_id=q_ps.id, answer_text="Ans", performance_score=70.0, semantic_similarity=70.0, completeness_score=70.0)
    r_beh = InterviewResponse(session_id=session.id, question_id=q_beh.id, answer_text="Ans", performance_score=90.0, semantic_similarity=90.0, completeness_score=90.0)
    db_session.add_all([r_tech, r_ps, r_beh])
    db_session.commit()
    
    # Generate report
    report = generate_report(db_session, user.id, session.id, resume.id)
    
    assert report.technical_score == 80.0
    assert report.problem_solving_score == 70.0
    assert report.behavioral_score == 90.0
    assert report.interview_performance_score == 80.0 # (80+70+90)/3
    # comm = (0.6*80+0.4*80) -> 80, 70, 90 -> avg = 80
    assert report.communication_score == 80.0
    assert report.resume_skill_match_score == 85.0
    assert report.overall_readiness_score == 80.5 # 20 + 14 + 16 + 13.5 + 8.5 + 8 = 80.5

@patch('services.career_readiness.calculate_resume_match')
def test_generate_report_missing_categories(mock_resume_match, db_session):
    mock_resume_match.return_value = 85.0
    
    # Create test data without Behavioral
    user = User(name="Test2", email="test_readiness2@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    resume = Resume(user_id=user.id, extracted_text="skills")
    session = InterviewSession(user_id=user.id, target_job_role="Software Engineer", status="COMPLETED")
    db_session.add_all([resume, session])
    db_session.commit()
    
    q_tech = InterviewQuestion(target_job_role="Software Engineer", category="Technical", question_text="Q1")
    db_session.add(q_tech)
    db_session.commit()
    
    r_tech = InterviewResponse(session_id=session.id, question_id=q_tech.id, answer_text="Ans", performance_score=80.0, semantic_similarity=80.0, completeness_score=80.0)
    db_session.add(r_tech)
    db_session.commit()
    
    with pytest.raises(ValueError, match="Missing Problem Solving responses"):
        generate_report(db_session, user.id, session.id, resume.id)

def test_generate_report_incomplete_session(db_session):
    user = User(name="Test3", email="test_readiness3@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    resume = Resume(user_id=user.id, extracted_text="skills")
    session = InterviewSession(user_id=user.id, target_job_role="Software Engineer", status="IN_PROGRESS") # NOT COMPLETED
    db_session.add_all([resume, session])
    db_session.commit()
    
    with pytest.raises(ValueError, match="incomplete interview"):
        generate_report(db_session, user.id, session.id, resume.id)

def test_generate_report_wrong_ownership(db_session):
    user1 = User(name="U1", email="u1@example.com", password_hash="hash")
    user2 = User(name="U2", email="u2@example.com", password_hash="hash")
    db_session.add_all([user1, user2])
    db_session.commit()
    
    session = InterviewSession(user_id=user2.id, target_job_role="SE", status="COMPLETED")
    resume = Resume(user_id=user1.id, extracted_text="text")
    db_session.add_all([session, resume])
    db_session.commit()
    
    with pytest.raises(ValueError, match="Not authorized to access this interview session"):
        generate_report(db_session, user1.id, session.id, resume.id)
        
    session.user_id = user1.id
    db_session.commit()
    with pytest.raises(ValueError, match="Not authorized to access this resume"):
        generate_report(db_session, user1.id, session.id, resume.id+999) # Invalid resume

def test_generate_report_db_rollback(db_session):
    # If commit fails, it should rollback
    user = User(name="Rb", email="rb@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    session = InterviewSession(user_id=user.id, target_job_role="Software Engineer", status="COMPLETED")
    resume = Resume(user_id=user.id, extracted_text="text")
    db_session.add_all([session, resume])
    db_session.commit()
    
    q_tech = InterviewQuestion(target_job_role="Software Engineer", category="Technical", question_text="Q1")
    q_ps = InterviewQuestion(target_job_role="Software Engineer", category="Problem Solving", question_text="Q2")
    q_beh = InterviewQuestion(target_job_role="Software Engineer", category="Behavioral", question_text="Q3")
    db_session.add_all([q_tech, q_ps, q_beh])
    db_session.commit()
    
    r_tech = InterviewResponse(session_id=session.id, question_id=q_tech.id, answer_text="Ans", performance_score=80.0, semantic_similarity=80.0, completeness_score=80.0)
    r_ps = InterviewResponse(session_id=session.id, question_id=q_ps.id, answer_text="Ans", performance_score=70.0, semantic_similarity=70.0, completeness_score=70.0)
    r_beh = InterviewResponse(session_id=session.id, question_id=q_beh.id, answer_text="Ans", performance_score=90.0, semantic_similarity=90.0, completeness_score=90.0)
    db_session.add_all([r_tech, r_ps, r_beh])
    db_session.commit()
    
    with patch('services.career_readiness.calculate_resume_match') as mock_resume, \
         patch.object(db_session, 'commit', side_effect=Exception("DB Error")):
        mock_resume.return_value = 85.0
        with pytest.raises(RuntimeError, match="Database persistence failed"):
            generate_report(db_session, user.id, session.id, resume.id)
