"""
Analytics service for HireMind Milestone 10: Dashboard & Analytics.

Aggregates deterministic interview statistics, category performances,
resume data, and career readiness progression for the authenticated user.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.user import User
from models.resume import Resume
from models.interview import InterviewSession, InterviewResponse, InterviewQuestion
from models.readiness import CareerReadinessReport
from services.career_readiness import (
    generate_recommendations,
    get_component_recommendations
)


def get_dashboard_analytics(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Retrieve and calculate all dashboard metrics for the given user.

    Strictly scoped to the provided user_id to ensure complete data isolation.
    Returns None for non-existent analytics rather than presenting misleading default values.
    """
    # 1. Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found.")

    # 2. Interview Sessions
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.started_at.desc(), InterviewSession.id.desc())
        .all()
    )

    total_sessions = len(sessions)
    completed_interviews = sum(1 for s in sessions if s.status == "COMPLETED")
    in_progress_interviews = sum(1 for s in sessions if s.status != "COMPLETED")

    # 3. Interview Responses and Category Performance
    # Join responses with questions and sessions filtered strictly by authenticated user_id
    responses_query = (
        db.query(
            InterviewResponse.performance_score,
            InterviewQuestion.category,
            InterviewResponse.session_id
        )
        .join(InterviewQuestion, InterviewResponse.question_id == InterviewQuestion.id)
        .join(InterviewSession, InterviewResponse.session_id == InterviewSession.id)
        .filter(InterviewSession.user_id == user_id)
        .all()
    )

    total_responses = len(responses_query)
    all_scores = [r[0] for r in responses_query if r[0] is not None]
    average_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else None

    # Group response scores by category
    tech_scores = [r[0] for r in responses_query if r[1] == "Technical" and r[0] is not None]
    ps_scores = [r[0] for r in responses_query if r[1] == "Problem Solving" and r[0] is not None]
    beh_scores = [r[0] for r in responses_query if r[1] == "Behavioral" and r[0] is not None]

    category_performance = {
        "technical_average": round(sum(tech_scores) / len(tech_scores), 2) if tech_scores else None,
        "problem_solving_average": round(sum(ps_scores) / len(ps_scores), 2) if ps_scores else None,
        "behavioral_average": round(sum(beh_scores) / len(beh_scores), 2) if beh_scores else None,
    }

    # Group response scores by session_id for recent interviews
    session_scores: Dict[int, List[float]] = {}
    for score, _, s_id in responses_query:
        if score is not None:
            session_scores.setdefault(s_id, []).append(score)

    recent_interviews = []
    for s in sessions[:5]:
        s_scores = session_scores.get(s.id, [])
        s_avg = round(sum(s_scores) / len(s_scores), 2) if s_scores else None
        recent_interviews.append({
            "id": s.id,
            "target_job_role": s.target_job_role,
            "status": s.status,
            "current_difficulty": s.current_difficulty,
            "started_at": s.started_at,
            "completed_at": s.completed_at,
            "response_count": len(s_scores),
            "average_score": s_avg
        })

    # 4. Resume Statistics
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc(), Resume.id.desc())
        .all()
    )

    resume_count = len(resumes)
    latest_resume_info = None
    extracted_skills = []

    if resumes:
        latest_r = resumes[0]
        skills_list = latest_r.skills if isinstance(latest_r.skills, list) else []
        extracted_skills = skills_list
        latest_resume_info = {
            "id": latest_r.id,
            "original_filename": latest_r.original_filename,
            "file_type": latest_r.file_type,
            "created_at": latest_r.created_at,
            "skills_count": len(skills_list)
        }

    # 5. Career Readiness Statistics
    reports = (
        db.query(CareerReadinessReport)
        .filter(CareerReadinessReport.user_id == user_id)
        .order_by(CareerReadinessReport.generated_at.desc(), CareerReadinessReport.id.desc())
        .all()
    )

    latest_report = None
    overall_readiness_score = None
    readiness_tier = None
    history = []

    if reports:
        latest_rep = reports[0]
        overall_readiness_score = latest_rep.overall_readiness_score

        # Map to the 4 standardized tiers
        if overall_readiness_score >= 85:
            readiness_tier = "Strong"
        elif overall_readiness_score >= 70:
            readiness_tier = "Solid"
        elif overall_readiness_score >= 50:
            readiness_tier = "Developing"
        else:
            readiness_tier = "Needs substantial improvement"

        recs = generate_recommendations(
            latest_rep.technical_score,
            latest_rep.problem_solving_score,
            latest_rep.communication_score,
            latest_rep.behavioral_score,
            latest_rep.resume_skill_match_score,
            latest_rep.interview_performance_score
        )
        comp_recs = get_component_recommendations(
            latest_rep.technical_score,
            latest_rep.problem_solving_score,
            latest_rep.communication_score,
            latest_rep.behavioral_score,
            latest_rep.resume_skill_match_score,
            latest_rep.interview_performance_score
        )

        latest_report = {
            "id": latest_rep.id,
            "report_id": latest_rep.id,
            "target_job_role": latest_rep.target_job_role,
            "overall_readiness_score": latest_rep.overall_readiness_score,
            "technical_score": latest_rep.technical_score,
            "problem_solving_score": latest_rep.problem_solving_score,
            "communication_score": latest_rep.communication_score,
            "behavioral_score": latest_rep.behavioral_score,
            "resume_skill_match_score": latest_rep.resume_skill_match_score,
            "interview_performance_score": latest_rep.interview_performance_score,
            "recommendations": recs,
            "component_recommendations": comp_recs,
            "generated_at": latest_rep.generated_at
        }

        # Historical reports ordered chronologically for performance progression charts
        history = [
            {
                "id": rep.id,
                "target_job_role": rep.target_job_role,
                "overall_readiness_score": rep.overall_readiness_score,
                "technical_score": rep.technical_score,
                "problem_solving_score": rep.problem_solving_score,
                "communication_score": rep.communication_score,
                "behavioral_score": rep.behavioral_score,
                "resume_skill_match_score": rep.resume_skill_match_score,
                "interview_performance_score": rep.interview_performance_score,
                "generated_at": rep.generated_at
            }
            for rep in reversed(reports)
        ]

    return {
        "user_id": user.id,
        "user_name": user.name,
        "target_job_role": user.target_job_role,
        "interview_stats": {
            "total_sessions": total_sessions,
            "completed_interviews": completed_interviews,
            "in_progress_interviews": in_progress_interviews,
            "total_responses": total_responses,
            "average_score": average_score
        },
        "category_performance": category_performance,
        "resume_stats": {
            "resume_count": resume_count,
            "latest_resume": latest_resume_info,
            "extracted_skills": extracted_skills
        },
        "career_readiness": {
            "latest_report": latest_report,
            "overall_readiness_score": overall_readiness_score,
            "readiness_tier": readiness_tier,
            "history": history
        },
        "recent_interviews": recent_interviews
    }
