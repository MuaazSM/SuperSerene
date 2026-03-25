"""Repository for analytics check-ins and metrics storage."""

from datetime import datetime, timezone
from typing import Dict, Any

from db.repositories.base_repository import BaseRepository


class AnalyticsRepository(BaseRepository):
    """Persist analytics data such as daily check-ins."""

    COLLECTION_NAME = "analytics"

    async def insert_checkin(self, user_id: str, payload: Dict[str, Any], mood_index: float) -> Dict[str, Any]:
        record = {
            **payload,
            "user_id": user_id,
            "mood_index": mood_index,
            "created_at": datetime.now(timezone.utc),
        }
        self.get_collection().insert_one(record)
        return {"mood_index": mood_index}
