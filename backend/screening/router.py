"""
Screening API endpoints.

- GET  /instruments                     — list available instruments
- GET  /{instrument}/questions          — questions + options for one instrument
- POST /{instrument}/score              — score answers, persist result
- POST /composite                       — score all instruments, return composite triage
"""

from datetime import datetime, timezone
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.deps import get_db, get_current_user, get_optional_current_user
from screening.instruments import (
    INSTRUMENTS,
    CARE_LEVELS,
    get_instrument,
    composite_triage,
)
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ScoreRequest(BaseModel):
    answers: List[int]


class CompositeRequest(BaseModel):
    PHQ_A: List[int] | None = None
    GAD_7: List[int] | None = None
    CRAFFT: List[int] | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _persist_result(db, user_id: str | None, instrument: str, answers: List[int], result: Dict[str, Any]):
    """Store screening result in MongoDB."""
    try:
        doc = {
            "user_id": user_id or "anonymous",
            "instrument": instrument,
            "answers": answers,
            "raw_score": result["raw_score"],
            "max_score": result["max_score"],
            "severity_band": result["severity_band"],
            "severity_label": result["severity_label"],
            "care_level": result["care_level"],
            "timestamp": datetime.now(timezone.utc),
        }
        db.db.screening_results.insert_one(doc)
    except Exception as e:
        _LOG.warning("Failed to persist screening result", error=str(e))


def _ensure_index(db):
    """Create index on screening_results if needed (idempotent)."""
    try:
        db.db.screening_results.create_index(
            [("user_id", 1), ("timestamp", -1)],
            name="user_screening_by_date",
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/instruments", tags=["screening"])
async def list_instruments():
    """Return metadata for all available screening instruments."""
    return {
        "instruments": [
            {
                "id": cls.NAME,
                "full_name": cls.FULL_NAME,
                "description": cls.DESCRIPTION,
                "num_questions": cls.NUM_QUESTIONS,
            }
            for cls in INSTRUMENTS.values()
        ],
        "care_levels": CARE_LEVELS,
    }


@router.get("/{instrument}/questions", tags=["screening"])
async def get_questions(instrument: str):
    """Return the question set for a given instrument."""
    try:
        cls = get_instrument(instrument)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return cls.get_questions()


@router.post("/{instrument}/score", tags=["screening"])
async def score_instrument(
    instrument: str,
    body: ScoreRequest,
    db=Depends(get_db),
    user=Depends(get_optional_current_user),
):
    """Score answers for a single instrument and persist the result."""
    try:
        cls = get_instrument(instrument)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        result = cls.score(body.answers)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    user_id = user.get("user_id") if user else None
    _ensure_index(db)
    _persist_result(db, user_id, instrument, body.answers, result.to_dict())

    return result.to_dict()


@router.post("/composite", tags=["screening"])
async def composite_score(
    body: CompositeRequest,
    db=Depends(get_db),
    user=Depends(get_optional_current_user),
):
    """Score multiple instruments and return a composite triage result."""
    scored = []
    user_id = user.get("user_id") if user else None
    _ensure_index(db)

    for field_name in ("PHQ_A", "GAD_7", "CRAFFT"):
        answers = getattr(body, field_name, None)
        if answers is None:
            continue
        try:
            cls = get_instrument(field_name)
            result = cls.score(answers)
            scored.append(result)
            _persist_result(db, user_id, field_name, answers, result.to_dict())
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name}: {e}",
            )

    if not scored:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide answers for at least one instrument (PHQ_A, GAD_7, or CRAFFT).",
        )

    return composite_triage(scored)
