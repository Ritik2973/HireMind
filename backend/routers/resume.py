import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.connection import get_db
from models.user import User
from models.resume import Resume
from schemas.resume import ResumeResponse, ResumeDetailResponse
from security.deps import get_current_user
from services.resume_parser import extract_text_from_pdf, extract_skills

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024 # 5 MB

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    original_filename = file.filename if file.filename else "unnamed_resume.pdf"
        
    if not original_filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(status_code=422, detail="Only PDF files are supported")
        
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="File is empty")
        
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds the 5MB limit")
        
    # Generate safe server-side filename
    safe_filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Parse PDF (happens before saving to disk to prevent saving invalid files)
    try:
        extracted_text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    if not extracted_text:
        raise HTTPException(status_code=422, detail="No extractable text found in the PDF. Please upload a text-based PDF.")
        
    skills = extract_skills(extracted_text)
    
    # Save file safely
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    
    # Save to PostgreSQL DB
    new_resume = Resume(
        user_id=current_user.id,
        original_filename=original_filename,
        file_type="application/pdf",
        file_path=file_path,
        extracted_text=extracted_text,
        skills=skills
    )
    
    try:
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
    except Exception:
        db.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the resume."
        )
    
    return ResumeResponse(
        id=new_resume.id,
        user_id=new_resume.user_id,
        original_filename=new_resume.original_filename,
        file_type=new_resume.file_type,
        skills=new_resume.skills,
        created_at=new_resume.created_at,
        extracted_text_length=len(new_resume.extracted_text)
    )

@router.get("", response_model=list[ResumeResponse])
def get_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resumes = db.execute(select(Resume).where(Resume.user_id == current_user.id)).scalars().all()
    
    results = []
    for r in resumes:
        results.append(ResumeResponse(
            id=r.id,
            user_id=r.user_id,
            original_filename=r.original_filename,
            file_type=r.file_type,
            skills=r.skills or [],
            created_at=r.created_at,
            extracted_text_length=len(r.extracted_text) if r.extracted_text else 0
        ))
    return results

@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.execute(select(Resume).where(Resume.id == resume_id)).scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # User ownership enforcement
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resume")
        
    return ResumeDetailResponse(
        id=resume.id,
        user_id=resume.user_id,
        original_filename=resume.original_filename,
        file_type=resume.file_type,
        skills=resume.skills or [],
        created_at=resume.created_at,
        extracted_text_length=len(resume.extracted_text) if resume.extracted_text else 0,
        extracted_text=resume.extracted_text
    )
