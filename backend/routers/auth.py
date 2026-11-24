# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import select

from database.connection import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, UserLogin, Token
from security.hashing import get_password_hash, verify_password
from security.jwt import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if email already exists
    existing_user = db.execute(select(User).where(User.email == user_data.email)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(        
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )
    
    # 2. Hash password securely
    hashed_password = get_password_hash(user_data.password)
    
    # 3. Create User object (excluding plain password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        target_job_role=user_data.target_job_role
    )
    
    # 4. Save to DB
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user."
        )
        
    return new_user

@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    # Generic error for both not found and wrong password
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password"
    )
    
    # 1. Find user by email
    user = db.execute(select(User).where(User.email == user_credentials.email)).scalar_one_or_none()
    
    if not user:
        raise credentials_exception
        
    # 2. Verify submitted password against password_hash
    if not verify_password(user_credentials.password, user.password_hash):
        raise credentials_exception
        
    # 3. Create JWT access token
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )
    
    # 4. Return token
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, required by Swagger UI.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Find user by email (mapped to form_data.username)
    user = db.execute(select(User).where(User.email == form_data.username)).scalar_one_or_none()
    
    if not user:
        raise credentials_exception
        
    # 2. Verify password
    if not verify_password(form_data.password, user.password_hash):
        raise credentials_exception
        
    # 3. Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

from security.deps import get_current_user

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Returns the safe profile data of the currently authenticated user.
    """
    return current_user
