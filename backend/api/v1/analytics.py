"""Analytics API routes using service layer.

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

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, Dict, Any

from api.deps import get_current_user, get_optional_current_user, get_db, get_orchestrator
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
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: Optional[Dict] = Depends(get_optional_current_user),
):
    try:
        user_id = current_user.get("user_id") if current_user else payload.get("user_id", "anonymous")
        result = await service.submit_checkin(user_id=user_id, payload=payload)
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
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: Optional[Dict] = Depends(get_optional_current_user),
):
    try:
        lookup_user_id = user_id or (current_user.get("user_id") if current_user else "anonymous")
        return await service.mood_timeline(user_id=lookup_user_id, session_id=session_id, limit=limit)
    except Exception as e:
        _LOG.error("Failed to compute mood timeline", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute mood timeline"
        )
