import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.connection import get_db          
from routers import auth, user, resume, ml, interview, career_readiness, analytics

logger = logging.getLogger("hiremind")

app = FastAPI(
    title="HireMind API",
    description="Backend for the AI-Based Adaptive Interview Analyzer",
    version="0.1.0"
)

# Configure CORS dynamically with secure development and environment defaults
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler to prevent leaking internal tracebacks
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."}
    )

# Include API Routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(resume.router)
app.include_router(ml.router)
app.include_router(interview.router)
app.include_router(career_readiness.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the HireMind API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/db-test")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            return {"status": "success", "message": "Successfully connected to PostgreSQL database 'hiremind'"}
        else:
            raise HTTPException(status_code=500, detail="Database query did not return expected result")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
