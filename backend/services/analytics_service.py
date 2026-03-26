"""Analytics service for user metrics and dashboards."""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List

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
            return analytics_core.get_activation_stats(days=days)
        except Exception as e:
            self.log_warning("Activation metric failed", error=str(e))
            return {"activation": [], "error": "activation_unavailable"}

    async def retention(self, days: int = 7) -> Dict[str, Any]:
        try:
            return analytics_core.get_retention_stats(days=days)
        except Exception as e:
            self.log_warning("Retention metric failed", error=str(e))
            return {"retention": [], "error": "retention_unavailable"}

    async def helpfulness(self) -> Dict[str, Any]:
        try:
            return analytics_core.get_helpfulness_stats()
        except Exception as e:
            self.log_warning("Helpfulness metric failed", error=str(e))
            return {"helpfulness": [], "error": "helpfulness_unavailable"}

    async def safety(self) -> Dict[str, Any]:
        try:
            return analytics_core.get_safety_stats()
        except Exception as e:
            self.log_warning("Safety metric failed", error=str(e))
            return {"safety": [], "error": "safety_unavailable"}

    async def summary(self) -> Dict[str, Any]:
        try:
            activation = analytics_core.get_activation_stats()
            retention = analytics_core.get_retention_stats()
            helpfulness = analytics_core.get_helpfulness_stats()
            safety = analytics_core.get_safety_stats()
            return {
                "activation": activation,
                "retention": retention,
                "helpfulness": helpfulness,
                "safety": safety,
            }
        except Exception as e:
            self.log_warning("Summary metric failed", error=str(e))
            return {"summary": {}, "error": "summary_unavailable"}

    async def series(self, start_date: Optional[str], end_date: Optional[str]) -> Dict[str, Any]:
        try:
            repo = AnalyticsRepository(self.db)
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None
            mood_indices: List[float] = await repo.get_mood_indices(start_dt=start_dt, end_dt=end_dt)
            stats = analytics_core.compute_series_stats(mood_indices)
            return {"series": mood_indices, **stats}
        except Exception as e:
            self.log_warning("Series metric failed", error=str(e))
            return {"series": [], "error": "series_unavailable"}

    async def mood_timeline(self, user_id: str, session_id: Optional[str], limit: int) -> Dict[str, Any]:
        try:
            repo = AnalyticsRepository(self.db)
            timeline = await repo.get_mood_timeline(user_id=user_id, session_id=session_id, limit=limit)
            return {"timeline": timeline}
        except Exception as e:
            self.log_warning("Mood timeline failed", error=str(e))
            return {"timeline": [], "error": "mood_timeline_unavailable"}
