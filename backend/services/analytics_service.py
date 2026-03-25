"""Analytics service for user metrics and dashboards."""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from services.base_service import BaseService
from core import analytics as analytics_core
from db.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService(BaseService):
    """Service wrapper around analytics functions."""

    async def get_checkin_questions(self) -> Dict[str, Any]:
        return {"questions": analytics_core.get_checkin_questions()}

    async def submit_checkin(self, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            mood_index = analytics_core.compute_mood_index(payload)
            repo = AnalyticsRepository(self.db)
            return await repo.insert_checkin(user_id=user_id, payload=payload, mood_index=mood_index)
        except Exception as e:
            self.log_warning("Check-in submission failed", error=str(e))
            return {"mood_index": 0.0, "stored": False, "error": "checkin_unavailable"}

    async def activation(self, days: int = 7) -> Dict[str, Any]:
        try:
            since = datetime.now(timezone.utc) - timedelta(days=days)
            return analytics_core.activation_metric(self.db, since)
        except Exception as e:
            self.log_warning("Activation metric failed", error=str(e))
            return {"activation": [], "error": "activation_unavailable"}

    async def retention(self, days: int = 7) -> Dict[str, Any]:
        try:
            since = datetime.now(timezone.utc) - timedelta(days=days)
            return analytics_core.retention_metric(self.db, since)
        except Exception as e:
            self.log_warning("Retention metric failed", error=str(e))
            return {"retention": [], "error": "retention_unavailable"}

    async def helpfulness(self) -> Dict[str, Any]:
        try:
            return analytics_core.helpfulness_metric(self.db)
        except Exception as e:
            self.log_warning("Helpfulness metric failed", error=str(e))
            return {"helpfulness": [], "error": "helpfulness_unavailable"}

    async def safety(self) -> Dict[str, Any]:
        try:
            return analytics_core.safety_metric(self.db)
        except Exception as e:
            self.log_warning("Safety metric failed", error=str(e))
            return {"safety": [], "error": "safety_unavailable"}

    async def summary(self) -> Dict[str, Any]:
        try:
            return analytics_core.summary_metrics(self.db)
        except Exception as e:
            self.log_warning("Summary metric failed", error=str(e))
            return {"summary": {}, "error": "summary_unavailable"}

    async def series(self, start_date: Optional[str], end_date: Optional[str]) -> Dict[str, Any]:
        try:
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None
            return analytics_core.time_series_metrics(self.db, start_dt, end_dt)
        except Exception as e:
            self.log_warning("Series metric failed", error=str(e))
            return {"series": [], "error": "series_unavailable"}

    async def mood_timeline(self, user_id: str, session_id: Optional[str], limit: int) -> Dict[str, Any]:
        try:
            return analytics_core.mood_timeline(self.db, user_id, session_id, limit)
        except Exception as e:
            self.log_warning("Mood timeline failed", error=str(e))
            return {"timeline": [], "error": "mood_timeline_unavailable"}
