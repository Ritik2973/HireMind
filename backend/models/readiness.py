from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from database.connection import Base
from sqlalchemy.orm import relationship

class CareerReadinessReport(Base):
    __tablename__ = "career_readiness_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    interview_session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="RESTRICT"), nullable=False)
    target_job_role = Column(String(255), nullable=False)

    technical_score = Column(Float, nullable=False)
    problem_solving_score = Column(Float, nullable=False)
    communication_score = Column(Float, nullable=False)
    behavioral_score = Column(Float, nullable=False)
    resume_skill_match_score = Column(Float, nullable=False)
    interview_performance_score = Column(Float, nullable=False)
    
    overall_readiness_score = Column(Float, nullable=False)

    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User")
    interview_session = relationship("InterviewSession")
    resume = relationship("Resume")
