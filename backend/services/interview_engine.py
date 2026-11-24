from sqlalchemy.orm import Session
from sqlalchemy import select
from models.interview import InterviewQuestion, InterviewSession, InterviewResponse, Difficulty, InterviewStatus
from typing import Optional
import datetime

def adjust_difficulty(current_difficulty: str, score: float) -> str:
    """
    Deterministic state-machine logic for adaptive difficulty transitions.
    score >= 80: increase difficulty
    60 <= score < 80: maintain difficulty
    score < 60: decrease difficulty
    """
    if score >= 80:
        if current_difficulty == Difficulty.EASY.value:
            return Difficulty.MEDIUM.value
        return Difficulty.HARD.value
    elif score >= 60:
        return current_difficulty
    else:
        if current_difficulty == Difficulty.HARD.value:
            return Difficulty.MEDIUM.value
        return Difficulty.EASY.value

def get_next_question(db: Session, session_id: int, target_role: str, desired_difficulty: str) -> Optional[InterviewQuestion]:
    """
    Selects the next unused question for the interview session based on the deterministic desired difficulty.
    If no question of the desired difficulty is left, falls back to another available question.
    """
    # Find IDs of questions already asked in this session
    asked_question_ids_query = select(InterviewResponse.question_id).where(InterviewResponse.session_id == session_id)
    asked_question_ids = db.execute(asked_question_ids_query).scalars().all()
    
    # Try finding an unused question matching the exact difficulty
    question_query = select(InterviewQuestion).where(
        InterviewQuestion.target_job_role == target_role,
        InterviewQuestion.difficulty == desired_difficulty,
        InterviewQuestion.id.not_in(asked_question_ids)
    ).order_by(InterviewQuestion.id.asc()).limit(1)
    
    next_question = db.execute(question_query).scalar_one_or_none()
    
    if next_question:
        return next_question
        
    # Fallback: if exhausted, pick ANY unused question for the role
    fallback_query = select(InterviewQuestion).where(
        InterviewQuestion.target_job_role == target_role,
        InterviewQuestion.id.not_in(asked_question_ids)
    ).order_by(InterviewQuestion.id.asc()).limit(1)
    
    return db.execute(fallback_query).scalar_one_or_none()

def start_interview(db: Session, user_id: int, target_job_role: str) -> InterviewSession:
    """
    Creates a new interview session and selects the first MEDIUM difficulty question.
    """
    session = InterviewSession(
        user_id=user_id,
        target_job_role=target_job_role,
        current_difficulty=Difficulty.MEDIUM.value,
        status=InterviewStatus.IN_PROGRESS.value
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Get first question
    first_q = get_next_question(db, session.id, target_job_role, Difficulty.MEDIUM.value)
    if first_q:
        session.current_question_id = first_q.id
    else:
        session.status = InterviewStatus.COMPLETED.value
        session.completed_at = datetime.datetime.now(datetime.timezone.utc)
        
    db.commit()
    db.refresh(session)
    
    return session

def submit_answer_and_advance(
    db: Session, 
    session: InterviewSession, 
    question_id: int, 
    answer_text: str, 
    evaluation_metadata: dict
) -> InterviewSession:
    """
    Records an answer and its AI evaluation, computes adaptive difficulty, selects the next question, 
    and handles interview completion.
    """
    if session.status == InterviewStatus.COMPLETED.value:
        raise ValueError("Interview is already completed.")
        
    if session.current_question_id != question_id:
        raise ValueError("Submitted question_id does not match the current question of the session.")

    score = evaluation_metadata["overall_score"]

    # Record the response
    response = InterviewResponse(
        session_id=session.id,
        question_id=question_id,
        answer_text=answer_text,
        performance_score=score,
        semantic_similarity=evaluation_metadata.get("semantic_similarity"),
        concept_coverage=evaluation_metadata.get("concept_coverage"),
        completeness_score=evaluation_metadata.get("completeness_score"),
        feedback=evaluation_metadata.get("feedback")
    )
    db.add(response)
    
    # Adapt difficulty based on score
    new_difficulty = adjust_difficulty(session.current_difficulty, score)
    session.current_difficulty = new_difficulty
    db.commit()
    
    # Select next question
    next_question = get_next_question(db, session.id, session.target_job_role, new_difficulty)
    
    if next_question:
        session.current_question_id = next_question.id
    else:
        session.status = InterviewStatus.COMPLETED.value
        session.completed_at = datetime.datetime.now(datetime.timezone.utc)
        session.current_question_id = None
        
    db.commit()
    db.refresh(session)
    return session
