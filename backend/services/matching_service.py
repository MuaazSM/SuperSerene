"""
Teletherapy matching service.

Matches users to licensed counselors based on screening results, specialty
alignment, availability, language, and rating.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from db.mongo import get_mongo
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)

# Day name helpers
_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _today_and_next(n: int = 2) -> List[str]:
    """Return lowercase day names for today and the next *n* days."""
    now = datetime.now(timezone.utc)
    return [_DAYS[(now.weekday() + i) % 7] for i in range(n + 1)]


def _user_concerns(user_id: str) -> List[str]:
    """Derive concern keywords from latest screening results."""
    mongo = get_mongo()
    results = list(
        mongo.db.screening_results.find({"user_id": user_id})
        .sort("timestamp", -1)
        .limit(3)
    )

    concerns: List[str] = []
    for r in results:
        inst = r.get("instrument", "")
        band = r.get("severity_band", "green")
        if inst == "PHQ_A" and band in ("yellow", "orange", "red"):
            concerns.append("depression")
        if inst == "GAD_7" and band in ("yellow", "orange", "red"):
            concerns.append("anxiety")
        if inst == "CRAFFT" and band in ("orange", "red"):
            concerns.append("substance_use")

    # Fallback to general
    if not concerns:
        concerns = ["general", "stress"]

    return list(set(concerns))


def _user_language(user_id: str) -> str:
    mongo = get_mongo()
    user = mongo.get_user(user_id) or mongo.db.users.find_one({"user_id": user_id}) or {}
    return user.get("language", "English")


def _score_provider(
    provider: Dict[str, Any],
    concerns: List[str],
    upcoming_days: List[str],
    user_lang: str,
) -> float:
    """
    Score a provider 0-1 based on:
      - specialty match  (weight 0.4)
      - availability     (weight 0.3)
      - language match   (weight 0.2)
      - rating           (weight 0.1)
    """
    # Specialty match (Jaccard-like)
    specs = set(s.lower() for s in provider.get("specialties", []))
    concern_set = set(c.lower() for c in concerns)
    if specs and concern_set:
        spec_score = len(specs & concern_set) / len(concern_set)
    else:
        spec_score = 0.2  # baseline for general providers

    # Availability in next 48h
    slots = provider.get("availability_slots", [])
    available_days = set(s.get("day", "").lower() for s in slots)
    upcoming_set = set(upcoming_days)
    if available_days:
        avail_score = len(available_days & upcoming_set) / max(len(upcoming_set), 1)
    else:
        avail_score = 0.0

    # Language match
    langs = [l.lower() for l in provider.get("languages", [])]
    lang_score = 1.0 if user_lang.lower() in langs else 0.0

    # Rating (normalise to 0-1)
    rating = provider.get("rating", 3.0)
    rating_score = min(rating / 5.0, 1.0)

    return (0.4 * spec_score) + (0.3 * avail_score) + (0.2 * lang_score) + (0.1 * rating_score)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def match_providers(user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Return top *limit* matched providers for the user, sorted by match score.
    """
    mongo = get_mongo()

    concerns = _user_concerns(user_id)
    upcoming = _today_and_next(2)
    lang = _user_language(user_id)

    providers = list(mongo.db.providers.find({"active": True}, {"_id": 0}))
    if not providers:
        _LOG.warning("No active providers in database")
        return []

    scored = []
    for p in providers:
        score = _score_provider(p, concerns, upcoming, lang)
        p["match_score"] = round(score, 3)
        # Compute next available slot text
        p["next_available"] = _next_slot_text(p.get("availability_slots", []), upcoming)
        scored.append(p)

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:limit]


def _next_slot_text(slots: List[Dict[str, Any]], upcoming: List[str]) -> str:
    for day in upcoming:
        for s in slots:
            if s.get("day", "").lower() == day:
                return f"{day.capitalize()} {s.get('start_time', '')} — {s.get('end_time', '')} {s.get('timezone', 'UTC')}"
    if slots:
        s = slots[0]
        return f"{s.get('day', '').capitalize()} {s.get('start_time', '')} — {s.get('end_time', '')} {s.get('timezone', 'UTC')}"
    return "Contact for availability"


def book_session(
    user_id: str,
    provider_id: str,
    day: str,
    start_time: str,
    end_time: str,
    timezone_str: str = "UTC",
) -> Dict[str, Any]:
    """Create a booking record and return confirmation."""
    mongo = get_mongo()

    provider = mongo.db.providers.find_one({"provider_id": provider_id, "active": True})
    if not provider:
        raise ValueError("Provider not found or inactive")

    booking_id = f"bk_{uuid.uuid4().hex[:12]}"
    platform = provider.get("teletherapy_platform", "zoom")

    # Generate a placeholder meeting link
    if platform == "zoom":
        meeting_link = f"https://zoom.us/j/{uuid.uuid4().hex[:10]}"
    elif platform == "meet":
        meeting_link = f"https://meet.google.com/{uuid.uuid4().hex[:12]}"
    else:
        meeting_link = f"https://superserene.app/session/{booking_id}"

    doc = {
        "booking_id": booking_id,
        "user_id": user_id,
        "provider_id": provider_id,
        "provider_name": provider.get("name", ""),
        "day": day,
        "start_time": start_time,
        "end_time": end_time,
        "timezone": timezone_str,
        "platform": platform,
        "meeting_link": meeting_link,
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc),
    }

    mongo.db.bookings.insert_one(doc)

    _LOG.info("Session booked", booking_id=booking_id, user_id=user_id, provider_id=provider_id)

    return {
        "booking_id": booking_id,
        "provider_name": provider.get("name"),
        "day": day,
        "start_time": start_time,
        "end_time": end_time,
        "timezone": timezone_str,
        "platform": platform,
        "meeting_link": meeting_link,
        "status": "confirmed",
    }


def get_user_bookings(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Return upcoming and past sessions for a user."""
    mongo = get_mongo()
    cursor = mongo.db.bookings.find(
        {"user_id": user_id},
        {"_id": 0},
    ).sort("created_at", -1).limit(limit)
    return list(cursor)


def cancel_booking(user_id: str, booking_id: str) -> bool:
    """Cancel a booking.  Returns True if found and updated."""
    mongo = get_mongo()
    result = mongo.db.bookings.update_one(
        {"booking_id": booking_id, "user_id": user_id, "status": "confirmed"},
        {"$set": {"status": "cancelled", "cancelled_at": datetime.now(timezone.utc)}},
    )
    return result.modified_count > 0
