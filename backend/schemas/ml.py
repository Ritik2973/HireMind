from pydantic import BaseModel

class AnalyzeResumeRequest(BaseModel):
    resume_id: int
    target_job_role: str

class AnalyzeResumeResponse(BaseModel):
    resume_id: int
    target_job_role: str
    semantic_similarity: float
    embedding_dimension: int
