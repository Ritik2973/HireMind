from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.connection import get_db
from models.user import User
from models.interview import InterviewSession, InterviewQuestion, InterviewStatus
from security.deps import get_current_user
from schemas.interview import (
    StartInterviewRequest, 
    SubmitAnswerRequest, 
    InterviewSessionResponse, 
    InterviewQuestionResponse
)
from services import interview_engine, answer_evaluator

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)

SUPPORTED_ROLES = [
    "Software Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Backend Developer",
    "Frontend Developer"
]

def _build_session_response(session: InterviewSession, latest_evaluation: dict = None) -> InterviewSessionResponse:
    q_resp = None
    if session.current_question:
        q_resp = InterviewQuestionResponse(
            id=session.current_question.id,
            question_text=session.current_question.question_text,
            category=session.current_question.category,
            difficulty=session.current_question.difficulty
        )
        
    return InterviewSessionResponse(
        id=session.id,
        target_job_role=session.target_job_role,
        current_difficulty=session.current_difficulty,
        status=session.status,
        current_question=q_resp,
        started_at=session.started_at,
        completed_at=session.completed_at,
        latest_evaluation=latest_evaluation
    )


@router.post("/start", response_model=InterviewSessionResponse)
def start_interview(
    request: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if request.target_job_role not in SUPPORTED_ROLES:
        raise HTTPException(status_code=422, detail=f"Unsupported job role: {request.target_job_role}")
        
    session = interview_engine.start_interview(db, current_user.id, request.target_job_role)
    return _build_session_response(session)


@router.get("/{session_id}", response_model=InterviewSessionResponse)
def get_interview(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.execute(select(InterviewSession).where(InterviewSession.id == session_id)).scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
        
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session.")
        
    return _build_session_response(session)


@router.post("/{session_id}/answer", response_model=InterviewSessionResponse)
def submit_answer(
    session_id: int,
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.execute(select(InterviewSession).where(InterviewSession.id == session_id)).scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
        
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session.")
        
    if session.status == InterviewStatus.COMPLETED or session.status == "COMPLETED" or not session.current_question:
        raise HTTPException(status_code=400, detail="Interview session is already completed.")

    if session.current_question_id != request.question_id:
        raise HTTPException(status_code=400, detail="Submitted question_id does not match the current question of the session.")

    # Run AI evaluation
    q = session.current_question
    eval_meta = answer_evaluator.evaluate_answer(
        candidate_text=request.answer_text,
        expected_answer=q.expected_answer or "",
        key_concepts=q.key_concepts or [],
        rubric_criteria=q.rubric_criteria or []
    )
        
    try:
        updated_session = interview_engine.submit_answer_and_advance(
            db=db,
            session=session,
            question_id=request.question_id,
            answer_text=request.answer_text,
            evaluation_metadata=eval_meta
        )
        return _build_session_response(updated_session, latest_evaluation=eval_meta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
