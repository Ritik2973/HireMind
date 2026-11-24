from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database.connection import Base

class Difficulty(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class InterviewStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_job_role = Column(String(100), nullable=False)
    
    current_difficulty = Column(String(50), default=Difficulty.MEDIUM.value, nullable=False)
    current_question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=True)
    status = Column(String(50), default=InterviewStatus.IN_PROGRESS.value, nullable=False)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    current_question = relationship("InterviewQuestion", foreign_keys=[current_question_id])
    responses = relationship("InterviewResponse", back_populates="session", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    target_job_role = Column(String(100), nullable=False)
    question_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False)
    
    # Milestone 8 Evaluation Metadata (Nullable for safe migration, enforced via seed script)
    expected_answer = Column(Text, nullable=True)
    key_concepts = Column(JSON, nullable=True)
    rubric_criteria = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Ensure uniqueness of questions per role to support idempotent seeding
    # No direct unique constraint on text across all rows, but combination can be unique.
    # We will handle idempotency in the seed script itself.


class InterviewResponse(Base):
    __tablename__ = "interview_responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)
    
    answer_text = Column(Text, nullable=False)
    performance_score = Column(Float, nullable=False)
    
    # Milestone 8 Evaluation Metadata
    semantic_similarity = Column(Float, nullable=True)
    concept_coverage = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("InterviewSession", back_populates="responses")
    question = relationship("InterviewQuestion")
