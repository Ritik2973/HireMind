import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Read SQL_ECHO from environment, default to False
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() in ("true", "1", "yes")

# Create the SQLAlchemy engine that manages the connection to PostgreSQL
engine = create_engine(DATABASE_URL, echo=SQL_ECHO, pool_pre_ping=True)

# Create a sessionmaker which will generate database sessions for our endpoints
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our future database models
Base = declarative_base()

# Dependency function to provide a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
