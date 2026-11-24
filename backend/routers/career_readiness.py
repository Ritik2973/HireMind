"""
Career Readiness API Router for HireMind Milestone 9.

Provides protected endpoints for generating and retrieving Career Readiness Reports.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from models.readiness import CareerReadinessReport
from security.deps import get_current_user
from schemas.readiness import CareerReadinessGenerateRequest, CareerReadinessReportResponse
from services.career_readiness import (
    generate_report,
    generate_recommendations,
    get_component_recommendations
)

router = APIRouter(
    prefix="/career-readiness",
    tags=["Career Readiness"]
)


def _build_report_response(report: CareerReadinessReport) -> CareerReadinessReportResponse:
    recs = generate_recommendations(
        report.technical_score,
        report.problem_solving_score,
        report.communication_score,
        report.behavioral_score,
        report.resume_skill_match_score,
        report.interview_performance_score
    )
    comp_recs = get_component_recommendations(
        report.technical_score,
        report.problem_solving_score,
        report.communication_score,
        report.behavioral_score,
        report.resume_skill_match_score,
        report.interview_performance_score
    )
    return CareerReadinessReportResponse(
        id=report.id,
        report_id=report.id,
        user_id=report.user_id,
        interview_session_id=report.interview_session_id,
        resume_id=report.resume_id,
        target_job_role=report.target_job_role,
        technical_score=report.technical_score,
        problem_solving_score=report.problem_solving_score,
        communication_score=report.communication_score,
        behavioral_score=report.behavioral_score,
        resume_skill_match_score=report.resume_skill_match_score,
        interview_performance_score=report.interview_performance_score,
        overall_readiness_score=report.overall_readiness_score,
        recommendations=recs,
        component_recommendations=comp_recs,
        generated_at=report.generated_at,
        created_at=report.created_at
    )


@router.post("/generate", response_model=CareerReadinessReportResponse, status_code=status.HTTP_200_OK)
def generate_career_readiness(
    request: CareerReadinessGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a Career Readiness Report based on a completed interview session and uploaded resume.
    """
    try:
        report = generate_report(
            db=db,
            user_id=current_user.id,
            session_id=request.interview_session_id,
            resume_id=request.resume_id
        )
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        elif "not authorized" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=err_msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return _build_report_response(report)


@router.get("/latest", response_model=CareerReadinessReportResponse, status_code=status.HTTP_200_OK)
def get_latest_career_readiness_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the most recent Career Readiness Report for the authenticated user.
    """
    report = db.query(CareerReadinessReport).filter(
        CareerReadinessReport.user_id == current_user.id
    ).order_by(CareerReadinessReport.generated_at.desc(), CareerReadinessReport.id.desc()).first()

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No career readiness report found for this user.")

    return _build_report_response(report)


@router.get("/session/{session_id}", response_model=CareerReadinessReportResponse, status_code=status.HTTP_200_OK)
def get_career_readiness_report_by_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the Career Readiness Report for a specific interview session.
    """
    report = db.query(CareerReadinessReport).filter(
        CareerReadinessReport.interview_session_id == session_id,
        CareerReadinessReport.user_id == current_user.id
    ).order_by(CareerReadinessReport.generated_at.desc(), CareerReadinessReport.id.desc()).first()

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No career readiness report found for this interview session.")

    return _build_report_response(report)


@router.get("/{report_id}", response_model=CareerReadinessReportResponse, status_code=status.HTTP_200_OK)
def get_career_readiness_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a generated Career Readiness Report by ID.
    Enforces that only the owner can retrieve their own report.
    """
    report = db.query(CareerReadinessReport).filter(CareerReadinessReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Career readiness report not found.")

    if report.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this report.")

    return _build_report_response(report)
