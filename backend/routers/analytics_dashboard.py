"""
Advanced analytics dashboard API.

- GET /timeline?period=week|month|3months
- GET /ema
- GET /facets
- GET /streaks
- GET /trends
- GET /export?period=month  (returns PDF)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response

from api.deps import get_current_user, get_optional_current_user
from services.analytics_dashboard import (
    get_mood_timeline,
    get_ema_overlays,
    get_facet_breakdown,
    get_streak_stats,
    detect_trends,
    export_pdf_report,
)
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)
router = APIRouter()


@router.get("/timeline", tags=["analytics-dashboard"])
async def timeline(
    period: str = Query("month", regex="^(week|month|3months)$"),
    user=Depends(get_optional_current_user),
):
    user_id = user.get("user_id") if user else "anonymous"
    try:
        return get_mood_timeline(user_id, period)
    except Exception as e:
        _LOG.error("Timeline failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get timeline")


@router.get("/ema", tags=["analytics-dashboard"])
async def ema_overlays(user=Depends(get_optional_current_user)):
    user_id = user.get("user_id") if user else "anonymous"
    try:
        return get_ema_overlays(user_id)
    except Exception as e:
        _LOG.error("EMA failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to compute EMA")


@router.get("/facets", tags=["analytics-dashboard"])
async def facets(user=Depends(get_optional_current_user)):
    user_id = user.get("user_id") if user else "anonymous"
    try:
        return get_facet_breakdown(user_id)
    except Exception as e:
        _LOG.error("Facets failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get facets")


@router.get("/streaks", tags=["analytics-dashboard"])
async def streaks(user=Depends(get_optional_current_user)):
    user_id = user.get("user_id") if user else "anonymous"
    try:
        return get_streak_stats(user_id)
    except Exception as e:
        _LOG.error("Streaks failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get streaks")


@router.get("/trends", tags=["analytics-dashboard"])
async def trends(user=Depends(get_optional_current_user)):
    user_id = user.get("user_id") if user else "anonymous"
    try:
        return detect_trends(user_id)
    except Exception as e:
        _LOG.error("Trends failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to detect trends")


@router.get("/export", tags=["analytics-dashboard"])
async def export_report(
    period: str = Query("month", regex="^(week|month|3months)$"),
    user=Depends(get_current_user),
):
    user_id = user.get("user_id")
    try:
        pdf_bytes = export_pdf_report(user_id, period)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=superserene_report_{period}.pdf"},
        )
    except Exception as e:
        _LOG.error("Export failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate report")
