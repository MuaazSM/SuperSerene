"""Exercise and wellness API routes using service layer."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from api.deps import get_current_user, get_db, get_orchestrator
from services.exercise_service import ExerciseService
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)

router = APIRouter()


def get_exercise_service(db=Depends(get_db), orchestrator=Depends(get_orchestrator)) -> ExerciseService:
    return ExerciseService(db=db, orchestrator=orchestrator)


@router.post("/recommendations", tags=["exercises"])
async def get_recommendations(
    request: dict,
    current_user: dict = Depends(get_current_user),
    service: ExerciseService = Depends(get_exercise_service),
):
    try:
        user_id = current_user.get("user_id")
        result = await service.recommend(
            user_id=user_id,
            mood=request.get("mood", 3),
            context=request.get("context", ""),
            energy_level=request.get("energy_level", 3),
            count=request.get("count", 3),
        )
        _LOG.info("Recommendations generated", user_id=user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _LOG.error("Failed to get exercise recommendations", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )


@router.get("/recommendations", tags=["exercises"])
async def list_recommendations(
    user_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: ExerciseService = Depends(get_exercise_service),
):
    try:
        lookup_user_id = user_id or current_user.get("user_id")
        return await service.list_recommendations(user_id=lookup_user_id, limit=limit, skip=skip)
    except Exception as e:
        _LOG.error("Failed to list recommendations", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list recommendations"
        )


@router.post("/rate", tags=["exercises"])
async def rate_exercise(
    request: dict,
    current_user: dict = Depends(get_current_user),
    service: ExerciseService = Depends(get_exercise_service),
):
    try:
        result = await service.rate(
            user_id=current_user.get("user_id"),
            exercise_id=request.get("exercise_id"),
            rating=request.get("rating"),
            feedback=request.get("feedback", ""),
        )
        _LOG.info("Exercise rated", user_id=current_user.get("user_id"))
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _LOG.error("Failed to rate exercise", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rate exercise"
        )


@router.get("/history", tags=["exercises"])
async def get_exercise_history(
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: ExerciseService = Depends(get_exercise_service),
):
    try:
        lookup_user_id = user_id or current_user.get("user_id")
        return await service.history(user_id=lookup_user_id, limit=limit, skip=skip)
    except Exception as e:
        _LOG.error("Failed to get exercise history", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get history"
        )
