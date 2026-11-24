from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
import datetime

class CareerReadinessGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    interview_session_id: int
    resume_id: int

CareerReadinessAnalyzeRequest = CareerReadinessGenerateRequest

class CareerReadinessReportResponse(BaseModel):
    id: int
    report_id: int
    user_id: int
    interview_session_id: int
    resume_id: int
    target_job_role: str
    
    technical_score: float
    problem_solving_score: float
    communication_score: float
    behavioral_score: float
    resume_skill_match_score: float
    interview_performance_score: float
    overall_readiness_score: float
    
    recommendations: List[str]
    component_recommendations: Dict[str, str]
    
    generated_at: datetime.datetime
    created_at: datetime.datetime

class ReadinessComponent(BaseModel):
    score: Optional[float]
    available: bool
    sample_count: int

class CareerReadinessResponse(BaseModel):
    report_id: int
    target_job_role: str
    overall_readiness_score: float
    
    technical_knowledge: ReadinessComponent
    problem_solving: ReadinessComponent
    communication: ReadinessComponent
    behavioral_readiness: ReadinessComponent
    resume_skill_match: ReadinessComponent
    interview_performance: ReadinessComponent
    
    recommendations: List[str]
    generated_at: datetime.datetime
