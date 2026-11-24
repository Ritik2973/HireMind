from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class StartInterviewRequest(BaseModel):
    target_job_role: str

class SubmitAnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    question_id: int
    answer_text: str = Field(..., min_length=1)

class InterviewQuestionResponse(BaseModel):
    id: int
    question_text: str
    category: str
    difficulty: str

class EvaluationComponent(BaseModel):
    semantic_similarity: float
    concept_coverage: float
    completeness_score: float
    feedback: str
    overall_score: float

class InterviewSessionResponse(BaseModel):
    id: int
    target_job_role: str
    current_difficulty: str
    status: str
    current_question: Optional[InterviewQuestionResponse] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    latest_evaluation: Optional[EvaluationComponent] = None
