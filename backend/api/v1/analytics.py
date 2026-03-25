"""Analytics API routes.

Endpoints:
- GET /checkin/questions - Get check-in questions
- POST /checkin - Submit daily check-in
- GET /activation - Get activation metrics
- GET /retention - Get retention metrics
- GET /helpfulness - Get helpfulness metrics
- GET /safety - Get safety metrics
- GET /summary - Get analytics summary
- GET /series - Get time series data
- GET /mood_timeline - Get mood timeline
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional
from datetime import datetime, timezone

from api.deps import get_current_user, get_db
from db.mongo import Collections
from core.analytics import (
    get_activation_stats,
    get_retention_stats,
    get_helpfulness_stats,
    get_safety_stats
)
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)

router = APIRouter()


@router.get("/checkin/questions", tags=["analytics"])
async def get_checkin_questions():
    """Get daily check-in questions.
    
    Returns:
        List of 5-dimension EQ assessment questions
    """
    return {
        "questions": [
            {"id": "mood", "text": "How are you feeling today?", "scale": "1=Very Low, 5=Very High"},
            {"id": "stress", "text": "How stressed did you feel today?", "scale": "1=Not at all, 5=Extremely"},
            {"id": "energy", "text": "What's your energy level right now?", "scale": "1=Very Low, 5=Very High"},
            {"id": "connection", "text": "How connected did you feel to others today?", "scale": "1=Not at all, 5=Very Connected"},
            {"id": "motivation", "text": "How motivated did you feel today?", "scale": "1=Not at all, 5=Extremely"}
        ]
    }


"""Analytics API routes using service layer."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, Dict, Any

from api.deps import get_current_user, get_db, get_orchestrator
from services.analytics_service import AnalyticsService
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)

router = APIRouter()


def get_analytics_service(db=Depends(get_db), orchestrator=Depends(get_orchestrator)) -> AnalyticsService:
    return AnalyticsService(db=db, orchestrator=orchestrator)


@router.get("/checkin/questions", tags=["analytics"])
async def get_checkin_questions(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return await service.get_checkin_questions()
    except Exception as e:
        _LOG.error("Failed to get check-in questions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get questions"
        )


@router.post("/checkin", tags=["analytics"])
async def submit_checkin(
    payload: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        result = await service.submit_checkin(user_id=current_user.get("user_id"), payload=payload)
        return result
    except Exception as e:
        _LOG.error("Failed to submit check-in", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit check-in"
        )


@router.get("/activation", tags=["analytics"])
async def activation_metrics(
    days: int = Query(7, ge=1, le=90),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.activation(days=days)
    except Exception as e:
        _LOG.error("Failed to compute activation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute activation"
        )


@router.get("/retention", tags=["analytics"])
async def retention_metrics(
    days: int = Query(7, ge=1, le=90),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.retention(days=days)
    except Exception as e:
        _LOG.error("Failed to compute retention", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute retention"
        )


@router.get("/helpfulness", tags=["analytics"])
async def helpfulness_metrics(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return await service.helpfulness()
    except Exception as e:
        _LOG.error("Failed to compute helpfulness", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute helpfulness"
        )


@router.get("/safety", tags=["analytics"])
async def safety_metrics(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return await service.safety()
    except Exception as e:
        _LOG.error("Failed to compute safety metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute safety metrics"
        )


@router.get("/summary", tags=["analytics"])
async def summary_metrics(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return await service.summary()
    except Exception as e:
        _LOG.error("Failed to compute summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute summary"
        )


@router.get("/series", tags=["analytics"])
async def time_series_metrics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.series(start_date=start_date, end_date=end_date)
    except Exception as e:
        _LOG.error("Failed to compute time series", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute time series"
        )


@router.get("/mood_timeline", tags=["analytics"])
async def mood_timeline(
    user_id: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    current_user: Dict = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        lookup_user_id = user_id or current_user.get("user_id")
        return await service.mood_timeline(user_id=lookup_user_id, session_id=session_id, limit=limit)
    except Exception as e:
        _LOG.error("Failed to compute mood timeline", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute mood timeline"
        )

@router.get("/mood_timeline", tags=["analytics"])
async def get_mood_timeline(
    session_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Collections = Depends(get_db),
):
    """Get mood timeline for user or session.
    
    Args:
        session_id: Filter by session
        user_id: Filter by user
        days: Number of days to look back
        db: Database connection
        
    Returns:
        Mood timeline data
    """
    try:
        from datetime import timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        query = {"timestamp": {"$gte": cutoff}}
        
        if session_id:
            query["session_id"] = session_id
        if user_id:
            query["user_id"] = user_id
        
        data = list(db.analytics.find(query).sort("timestamp", 1))
        return {"mood_data": data, "days": days}
    except Exception as e:
        _LOG.error("Mood timeline failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get mood timeline"
        )
