from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.connection import get_db
from models.user import User
from security.jwt import verify_token

# This dependency automatically reads the Authorization header, expects a Bearer token
# and configures Swagger UI to use the form-data /auth/token endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Validates the JWT token from the request header and retrieves the corresponding user.
    Throws HTTP 401 if the token is missing, invalid, expired, or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify and decode the JWT
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        parsed_user_id = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception
        
    # Retrieve user from database
    user = db.execute(select(User).where(User.id == parsed_user_id)).scalar_one_or_none()
    if user is None:
        raise credentials_exception
        
    return user
