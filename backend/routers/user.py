from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.connection import get_db
from models.user import User
from schemas.user import UserResponse, UserUpdate
from security.deps import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users Profile"]
)

@router.get("/me", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Retrieve the authenticated user's profile.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_profile(
    profile_data: UserUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the authenticated user's profile information.
    """
    # If updating email, check for duplicates
    if profile_data.email and profile_data.email != current_user.email:
        existing_user = db.execute(
            select(User).where(User.email == profile_data.email)
        ).scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already in use by another account"
            )
        current_user.email = profile_data.email

    if profile_data.name is not None:
        current_user.name = profile_data.name
        
    if profile_data.target_job_role is not None:
        current_user.target_job_role = profile_data.target_job_role

    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the profile."
        )

    return current_user
