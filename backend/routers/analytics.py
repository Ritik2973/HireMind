"""
Analytics API Router for HireMind Milestone 10: Dashboard & Analytics.

Provides protected endpoints for aggregated candidate analytics and performance trends.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from security.deps import get_current_user
from schemas.analytics import DashboardAnalyticsResponse
from services.analytics import get_dashboard_analytics

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/dashboard", response_model=DashboardAnalyticsResponse, status_code=status.HTTP_200_OK)
def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve aggregated dashboard metrics, category performance, resume status,
    and career readiness progression for the authenticated user.
    """
    try:
        return get_dashboard_analytics(db=db, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating dashboard analytics: {str(e)}"
        )
