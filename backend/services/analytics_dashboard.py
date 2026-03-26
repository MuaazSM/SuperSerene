"""
Advanced mood analytics dashboard service.

Provides timeline data, EMA overlays, facet breakdowns, streak stats,
trend detection, and PDF export.
"""

import io
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from db.mongo import get_mongo
from core.analytics import ema, zscore, compute_series_stats
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)

_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_FACETS = ["mood", "stress", "energy", "connection", "motivation"]

PERIOD_DAYS = {"week": 7, "month": 30, "3months": 90}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _checkins(user_id: str, days: int) -> List[Dict[str, Any]]:
    """Fetch checkin records for a user within the last N days."""
    mongo = get_mongo()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cursor = mongo.db.analytics.find(
        {"user_id": user_id, "created_at": {"$gte": cutoff}},
        {"_id": 0},
    ).sort("created_at", 1)
    return list(cursor)


def _all_checkins(user_id: str) -> List[Dict[str, Any]]:
    """Fetch all checkin records for a user."""
    mongo = get_mongo()
    cursor = mongo.db.analytics.find(
        {"user_id": user_id},
        {"_id": 0},
    ).sort("created_at", 1)
    return list(cursor)


def _ema_series(values: List[float], k: int) -> List[float]:
    """Compute a running EMA series (not just the last value)."""
    if not values:
        return []
    alpha = 2.0 / (k + 1)
    result = [values[0]]
    for v in values[1:]:
        result.append(round(alpha * v + (1 - alpha) * result[-1], 2))
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_mood_timeline(user_id: str, period: str = "month") -> Dict[str, Any]:
    """
    Daily mood index + individual facet scores for a time period.
    """
    days = PERIOD_DAYS.get(period, 30)
    records = _checkins(user_id, days)

    timeline = []
    for r in records:
        ts = r.get("created_at")
        date_str = ts.strftime("%Y-%m-%d") if isinstance(ts, datetime) else str(ts)[:10]
        timeline.append({
            "date": date_str,
            "mood_index": round(r.get("mood_index", 0), 2),
            "mood": r.get("mood", 0),
            "stress": r.get("stress", 0),
            "energy": r.get("energy", 0),
            "connection": r.get("connection", 0),
            "motivation": r.get("motivation", 0),
        })

    return {"period": period, "days": days, "data": timeline}


def get_ema_overlays(user_id: str) -> Dict[str, Any]:
    """
    7-day and 14-day EMA series over mood index history.
    """
    records = _all_checkins(user_id)
    mood_values = [r.get("mood_index", 50) for r in records]

    dates = []
    for r in records:
        ts = r.get("created_at")
        dates.append(ts.strftime("%Y-%m-%d") if isinstance(ts, datetime) else str(ts)[:10])

    ema7 = _ema_series(mood_values, 7)
    ema14 = _ema_series(mood_values, 14)

    overlay = []
    for i, d in enumerate(dates):
        overlay.append({
            "date": d,
            "mood_index": round(mood_values[i], 2) if i < len(mood_values) else 0,
            "ema7": ema7[i] if i < len(ema7) else None,
            "ema14": ema14[i] if i < len(ema14) else None,
        })

    return {
        "data": overlay,
        "latest_ema7": ema7[-1] if ema7 else None,
        "latest_ema14": ema14[-1] if ema14 else None,
    }


def get_facet_breakdown(user_id: str) -> Dict[str, Any]:
    """
    Per-facet averages, trends, and self-percentile.
    """
    all_recs = _all_checkins(user_id)
    recent = _checkins(user_id, 7)

    facets = {}
    for facet in _FACETS:
        all_vals = [r.get(facet, 0) for r in all_recs if r.get(facet) is not None]
        recent_vals = [r.get(facet, 0) for r in recent if r.get(facet) is not None]

        avg_all = sum(all_vals) / len(all_vals) if all_vals else 0
        avg_recent = sum(recent_vals) / len(recent_vals) if recent_vals else 0

        # Trend: compare recent avg to overall avg
        if not all_vals or len(all_vals) < 3:
            trend = "stable"
        elif avg_recent > avg_all + 0.3:
            trend = "improving"
        elif avg_recent < avg_all - 0.3:
            trend = "declining"
        else:
            trend = "stable"

        # Self-percentile: what fraction of all-time values is <= current
        current = recent_vals[-1] if recent_vals else 0
        if all_vals:
            below = sum(1 for v in all_vals if v <= current)
            percentile = round((below / len(all_vals)) * 100)
        else:
            percentile = 50

        # Sparkline: last 14 values
        sparkline = [r.get(facet, 0) for r in all_recs[-14:]] if all_recs else []

        facets[facet] = {
            "average_all_time": round(avg_all, 2),
            "average_recent": round(avg_recent, 2),
            "current": current,
            "trend": trend,
            "percentile": percentile,
            "sparkline": sparkline,
        }

    return {"facets": facets}


def get_streak_stats(user_id: str) -> Dict[str, Any]:
    """
    Current streak, longest streak, total check-ins, average mood by day of week.
    """
    all_recs = _all_checkins(user_id)
    total = len(all_recs)

    # Extract unique dates
    dates_set = set()
    day_mood: Dict[int, List[float]] = {i: [] for i in range(7)}
    for r in all_recs:
        ts = r.get("created_at")
        if isinstance(ts, datetime):
            dates_set.add(ts.date())
            day_mood[ts.weekday()].append(r.get("mood_index", 50))

    sorted_dates = sorted(dates_set)

    # Compute streaks
    current_streak = 0
    longest_streak = 0
    streak = 0
    today = datetime.now(timezone.utc).date()
    for i, d in enumerate(sorted_dates):
        if i == 0:
            streak = 1
        else:
            if (d - sorted_dates[i - 1]).days == 1:
                streak += 1
            else:
                streak = 1
        longest_streak = max(longest_streak, streak)

    # Current streak: count back from today
    current_streak = 0
    check_date = today
    while check_date in dates_set:
        current_streak += 1
        check_date -= timedelta(days=1)

    # Avg mood by day
    mood_by_day = {}
    for i in range(7):
        vals = day_mood[i]
        mood_by_day[_DAYS[i]] = round(sum(vals) / len(vals), 1) if vals else 0

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_checkins": total,
        "mood_by_day": mood_by_day,
    }


def detect_trends(user_id: str) -> Dict[str, Any]:
    """
    Z-score trend detection:
    - Compute 7-day EMA
    - Compare against 30-day mean/std
    - Flag DECLINING (z <= -1.5), IMPROVING (z >= 1.5), or STABLE
    """
    month_recs = _checkins(user_id, 30)
    mood_values = [r.get("mood_index", 50) for r in month_recs]

    if len(mood_values) < 3:
        return {"trend": "STABLE", "zscore": 0.0, "message": "Not enough data for trend analysis."}

    ema7_val = ema(mood_values, 7)

    mean_30 = sum(mood_values) / len(mood_values)
    variance = sum((x - mean_30) ** 2 for x in mood_values) / len(mood_values)
    std_30 = math.sqrt(variance) if variance > 0 else 0

    if std_30 == 0:
        z = 0.0
    else:
        z = round((ema7_val - mean_30) / std_30, 3)

    if z <= -1.5:
        trend = "DECLINING"
        message = "Your mood has been declining over the past week. Consider reaching out for support."
    elif z >= 1.5:
        trend = "IMPROVING"
        message = "Great progress! Your mood has been trending upward recently."
    else:
        trend = "STABLE"
        message = "Your mood has been relatively stable."

    return {
        "trend": trend,
        "zscore": z,
        "ema7": ema7_val,
        "mean_30d": round(mean_30, 2),
        "std_30d": round(std_30, 2),
        "message": message,
    }


def export_pdf_report(user_id: str, period: str = "month") -> bytes:
    """
    Generate a PDF summary report.
    Uses reportlab for basic PDF generation.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib.colors import HexColor
    except ImportError:
        _LOG.warning("reportlab not installed — returning placeholder PDF")
        return _placeholder_pdf(user_id, period)

    timeline = get_mood_timeline(user_id, period)
    streaks = get_streak_stats(user_id)
    trends = detect_trends(user_id)
    facets = get_facet_breakdown(user_id)

    buf = io.BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 40 * mm

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20 * mm, y, f"SuperSerene — Mood Report ({period})")
    y -= 12 * mm

    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    y -= 10 * mm

    # Streaks
    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, y, "Overview")
    y -= 8 * mm
    c.setFont("Helvetica", 10)
    for label, val in [
        ("Current streak", f"{streaks['current_streak']} days"),
        ("Longest streak", f"{streaks['longest_streak']} days"),
        ("Total check-ins", str(streaks['total_checkins'])),
        ("Trend", trends['trend']),
        ("7-day EMA", str(trends.get('ema7', '—'))),
    ]:
        c.drawString(25 * mm, y, f"{label}: {val}")
        y -= 6 * mm

    y -= 6 * mm

    # Facet summary
    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, y, "Facet Breakdown")
    y -= 8 * mm
    c.setFont("Helvetica", 10)
    for facet, data in facets.get("facets", {}).items():
        c.drawString(25 * mm, y, f"{facet.capitalize()}: avg {data['average_recent']}, trend {data['trend']}, percentile {data['percentile']}%")
        y -= 6 * mm

    y -= 6 * mm

    # Timeline data (simple table)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, y, f"Daily Mood Index ({period})")
    y -= 8 * mm
    c.setFont("Helvetica", 9)
    for dp in timeline.get("data", [])[-30:]:
        if y < 30 * mm:
            c.showPage()
            y = h - 30 * mm
            c.setFont("Helvetica", 9)
        c.drawString(25 * mm, y, f"{dp['date']}  —  Mood: {dp['mood_index']}")
        y -= 5 * mm

    # Mood by day
    y -= 8 * mm
    if y < 60 * mm:
        c.showPage()
        y = h - 30 * mm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, y, "Average Mood by Day of Week")
    y -= 8 * mm
    c.setFont("Helvetica", 10)
    for day, val in streaks.get("mood_by_day", {}).items():
        c.drawString(25 * mm, y, f"{day}: {val}")
        y -= 6 * mm

    c.save()
    return buf.getvalue()


def _placeholder_pdf(user_id: str, period: str) -> bytes:
    """Minimal text-based PDF when reportlab is unavailable."""
    header = f"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    content = f"SuperSerene Mood Report ({period}) for user {user_id}. Install reportlab for charts."
    # Return a minimal valid-ish PDF
    return header.encode("utf-8")
