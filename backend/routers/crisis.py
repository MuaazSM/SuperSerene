"""
Crisis resources API — multi-language crisis hotline database.

- GET /resources?lang=en&country=US  — filtered resources
- GET /resources/all                  — full database grouped by language
- GET /nearest?lang=hi               — best-match resources for a language
"""

from fastapi import APIRouter, Query
from typing import Optional

from services.crisis_resources import (
    get_resources,
    get_all_grouped,
    get_nearest,
    LANGUAGE_NAMES,
    SUPPORTED_LANGUAGES,
)

router = APIRouter()


@router.get("/resources", tags=["crisis"])
async def resources(
    lang: Optional[str] = Query(None, description="Language code: en, hi, es, fr"),
    country: Optional[str] = Query(None, description="Country code: US, GB, IN, MX, FR, etc."),
):
    """Return crisis resources filtered by language and/or country."""
    data = get_resources(lang=lang, country_code=country)
    return {
        "resources": data,
        "count": len(data),
        "supported_languages": LANGUAGE_NAMES,
    }


@router.get("/resources/all", tags=["crisis"])
async def all_resources():
    """Return the full crisis resource database grouped by language."""
    grouped = get_all_grouped()
    return {
        "grouped": grouped,
        "supported_languages": LANGUAGE_NAMES,
        "total": sum(len(v) for v in grouped.values()),
    }


@router.get("/nearest", tags=["crisis"])
async def nearest(
    lang: str = Query("en", description="Preferred language code"),
):
    """Return crisis resources matching user's language, with English fallback."""
    return get_nearest(lang)
