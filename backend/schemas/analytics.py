"""
Pydantic schemas for HireMind Milestone 10: Dashboard & Analytics.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime


class InterviewStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_sessions: int
    completed_interviews: int
    in_progress_interviews: int
    total_responses: int
    average_score: Optional[float] = None


class CategoryPerformance(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    technical_average: Optional[float] = None
    problem_solving_average: Optional[float] = None
    behavioral_average: Optional[float] = None


class LatestResumeInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    file_type: str
    created_at: datetime
    skills_count: int


class ResumeStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resume_count: int
    latest_resume: Optional[LatestResumeInfo] = None
    extracted_skills: List[str] = []


class HistoricalReadinessReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    target_job_role: str
    overall_readiness_score: float
    technical_score: float
    problem_solving_score: float
    communication_score: float
    behavioral_score: float
    resume_skill_match_score: float
    interview_performance_score: float
    generated_at: datetime


class LatestReadinessReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_id: int
    target_job_role: str
    overall_readiness_score: float
    technical_score: float
    problem_solving_score: float
    communication_score: float
    behavioral_score: float
    resume_skill_match_score: float
    interview_performance_score: float
    recommendations: List[str] = []
    component_recommendations: Dict[str, str] = {}
    generated_at: datetime


class CareerReadinessStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latest_report: Optional[LatestReadinessReport] = None
    overall_readiness_score: Optional[float] = None
    readiness_tier: Optional[str] = None
    history: List[HistoricalReadinessReportItem] = []


class RecentInterviewItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    target_job_role: str
    status: str
    current_difficulty: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    response_count: int
    average_score: Optional[float] = None


class DashboardAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    user_name: str
    target_job_role: Optional[str] = None
    interview_stats: InterviewStats
    category_performance: CategoryPerformance
    resume_stats: ResumeStats
    career_readiness: CareerReadinessStats
    recent_interviews: List[RecentInterviewItem] = []
