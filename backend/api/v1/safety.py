"""Safety and crisis management API routes using service layer."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import Optional

from api.deps import get_current_user, get_db, get_orchestrator
from services.safety_service import SafetyService
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)

router = APIRouter()


def get_safety_service(db=Depends(get_db), orchestrator=Depends(get_orchestrator)) -> SafetyService:
    return SafetyService(db=db, orchestrator=orchestrator)


@router.post("/check", tags=["safety"])
async def safety_check(
    request: dict,
    current_user: dict = Depends(get_current_user),
    service: SafetyService = Depends(get_safety_service),
):
    """Lightweight wrapper to log a safety check request."""
    try:
        description = request.get("content") or request.get("description") or "Safety check"
        severity = request.get("severity", 2)
        immediate = request.get("immediate_risk", False)
        return await service.create_event(
            user_id=current_user.get("user_id"),
            description=description,
            severity=severity,
            immediate_risk=immediate,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _LOG.error("Safety check failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process safety check")


@router.post("/event", tags=["safety"])
async def create_safety_event(
    request: dict,
    current_user: dict = Depends(get_current_user),
    service: SafetyService = Depends(get_safety_service),
):
    try:
        result = await service.create_event(
            user_id=current_user.get("user_id"),
            description=request.get("description", ""),
            severity=request.get("severity", 2),
            immediate_risk=request.get("immediate_risk", False),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _LOG.error("Failed to create safety event", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event"
        )


@router.get("/events", tags=["safety"])
async def list_safety_events(
    user_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="open, resolved, closed"),
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: SafetyService = Depends(get_safety_service),
):
    try:
        lookup_user_id = user_id or current_user.get("user_id")
        return await service.list_events(user_id=lookup_user_id, status=status, limit=limit, skip=skip)
    except Exception as e:
        _LOG.error("Failed to list safety events", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list events"
        )


@router.get("/event/{event_id}", tags=["safety"])
async def get_safety_event(
    event_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    service: SafetyService = Depends(get_safety_service),
):
    try:
        result = await service.get_event(
            event_id=event_id,
            requester_id=current_user.get("user_id"),
            role=current_user.get("role", "user"),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        _LOG.error("Failed to get safety event", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get event"
        )


@router.post("/event/{event_id}/resolve", tags=["safety"])
async def resolve_safety_event(
    event_id: str = Path(...),
    request: dict = None,
    current_user: dict = Depends(get_current_user),
    service: SafetyService = Depends(get_safety_service),
):
    try:
        request = request or {}
        result = await service.resolve_event(
            event_id=event_id,
            requester_id=current_user.get("user_id"),
            role=current_user.get("role", "user"),
            outcome=request.get("outcome", "resolved"),
            notes=request.get("notes", ""),
            follow_up_needed=request.get("follow_up_needed", False),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        _LOG.error("Failed to resolve safety event", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve event"
        )


@router.post("/alerts/test", tags=["safety"])
async def test_alert_system(
    severity: int = Query(3, ge=1, le=5),
    current_user: dict = Depends(get_current_user),
    service: SafetyService = Depends(get_safety_service),
):
    try:
        result = await service.test_alert(user_id=current_user.get("user_id"), severity=severity)
        _LOG.info("Test alert sent", user_id=current_user.get("user_id"))
        return {"status": "sent" if result.get("sent") else "failed", **result}
    except Exception as e:
        _LOG.error("Failed to send test alert", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send alert"
        )
