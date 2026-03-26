"""
Teletherapy matching and booking API.

- GET    /matches                — matched providers for current user
- POST   /book                   — book a session
- GET    /bookings               — list user's bookings
- DELETE /bookings/{booking_id}  — cancel a booking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional

from api.deps import get_current_user, get_optional_current_user
from services.matching_service import match_providers, book_session, get_user_bookings, cancel_booking
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)
router = APIRouter()


class BookRequest(BaseModel):
    provider_id: str
    day: str
    start_time: str
    end_time: str
    timezone: str = "UTC"


@router.get("/matches", tags=["teletherapy"])
async def get_matches(
    limit: int = Query(3, ge=1, le=10),
    user=Depends(get_optional_current_user),
):
    """Return top matched providers for the current user."""
    user_id = user.get("user_id") if user else "anonymous"
    try:
        providers = match_providers(user_id, limit=limit)
        return {"providers": providers, "count": len(providers)}
    except Exception as e:
        _LOG.error("Matching failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to find matches")


@router.post("/book", tags=["teletherapy"])
async def book(
    body: BookRequest,
    user=Depends(get_current_user),
):
    """Book a teletherapy session with a provider."""
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID required")
    try:
        result = book_session(
            user_id=user_id,
            provider_id=body.provider_id,
            day=body.day,
            start_time=body.start_time,
            end_time=body.end_time,
            timezone_str=body.timezone,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        _LOG.error("Booking failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Booking failed")


@router.get("/bookings", tags=["teletherapy"])
async def list_bookings(
    user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
):
    """List current user's bookings."""
    user_id = user.get("user_id")
    return {"bookings": get_user_bookings(user_id, limit=limit)}


@router.delete("/bookings/{booking_id}", tags=["teletherapy"])
async def cancel(
    booking_id: str,
    user=Depends(get_current_user),
):
    """Cancel a booking."""
    user_id = user.get("user_id")
    if cancel_booking(user_id, booking_id):
        return {"ok": True, "booking_id": booking_id, "status": "cancelled"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found or already cancelled")
