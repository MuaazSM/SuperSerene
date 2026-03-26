"""
Guided meditation API.

- GET  /library                — all meditations grouped by duration
- GET  /recommended            — personalised top 3
- GET  /{id}                   — full session with steps
- POST /{id}/complete          — log completion with pre/post mood
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from api.deps import get_optional_current_user, get_current_user
from services.meditation_service import (
    get_library,
    get_meditation,
    recommend_meditations,
    log_completion,
)
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)
router = APIRouter()


class CompleteRequest(BaseModel):
    pre_mood: int   # 1-5
    post_mood: int  # 1-5


@router.get("/library", tags=["meditation"])
async def library():
    """Return all meditations grouped by duration tier."""
    return get_library()


@router.get("/recommended", tags=["meditation"])
async def recommended(
    limit: int = Query(3, ge=1, le=9),
    user=Depends(get_optional_current_user),
):
    """Return personalised meditation recommendations."""
    user_id = user.get("user_id") if user else "anonymous"
    return {"meditations": recommend_meditations(user_id, limit)}


@router.get("/{meditation_id}", tags=["meditation"])
async def get_session(meditation_id: str):
    """Return the full meditation session including steps."""
    m = get_meditation(meditation_id)
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meditation not found")
    return m


@router.post("/{meditation_id}/complete", tags=["meditation"])
async def complete(
    meditation_id: str,
    body: CompleteRequest,
    user=Depends(get_optional_current_user),
):
    """Log meditation completion with before/after mood rating."""
    if not get_meditation(meditation_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meditation not found")
    if body.pre_mood < 1 or body.pre_mood > 5 or body.post_mood < 1 or body.post_mood > 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Mood must be 1-5")

    user_id = user.get("user_id") if user else "anonymous"
    result = log_completion(user_id, meditation_id, body.pre_mood, body.post_mood)
    return result
