from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.connection import get_db
from models.user import User
from models.resume import Resume
from security.deps import get_current_user
from schemas.ml import AnalyzeResumeRequest, AnalyzeResumeResponse
from ml.services.semantic_analysis import analyze_resume_against_role

router = APIRouter(
    prefix="/ml",
    tags=["Machine Learning"]
)

@router.post("/analyze-resume", response_model=AnalyzeResumeResponse)
def analyze_resume_endpoint(
    request: AnalyzeResumeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch the resume from DB
    resume = db.execute(select(Resume).where(Resume.id == request.resume_id)).scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Enforce strict ownership boundaries
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to analyze this resume")
        
    if not resume.extracted_text:
        raise HTTPException(status_code=422, detail="This resume has no extracted text to analyze.")
        
    # Process through the ML pipeline
    try:
        results = analyze_resume_against_role(resume.extracted_text, request.target_job_role)
    except ValueError as e:
        # e.g., Unsupported job role or empty text
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Catch Model init / inference failures gracefully without exposing raw exceptions
        raise HTTPException(status_code=500, detail="An error occurred during ML analysis.")
        
    return AnalyzeResumeResponse(
        resume_id=resume.id,
        target_job_role=results["target_job_role"],
        semantic_similarity=results["semantic_similarity"],
        embedding_dimension=results["embedding_dimension"]
    )
