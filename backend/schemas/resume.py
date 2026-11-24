from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ResumeResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    file_type: str
    skills: List[str] = Field(default_factory=list)
    created_at: datetime
    extracted_text_length: int
    
    class Config:
        from_attributes = True

class ResumeDetailResponse(ResumeResponse):
    extracted_text: Optional[str] = None
