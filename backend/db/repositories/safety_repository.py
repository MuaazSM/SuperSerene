"""Repository for safety events and notes."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from bson import ObjectId

from db.repositories.base_repository import BaseRepository


class SafetyRepository(BaseRepository):
    """Manage safety events lifecycle."""

    COLLECTION_NAME = "safety_events"

    async def create_event(self, event: Dict[str, Any]) -> str:
        event.setdefault("status", "open")
        event.setdefault("created_at", datetime.now(timezone.utc))
        event.setdefault("updated_at", datetime.now(timezone.utc))
        result = self.get_collection().insert_one(event)
        return str(result.inserted_id)

    async def list_events(self, user_id: str, status: Optional[str], limit: int, skip: int) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"user_id": user_id}
        if status:
            query["status"] = status
        cursor = self.get_collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
        return list(cursor)

    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(event_id)
        except Exception:
            return None
        return self.get_collection().find_one({"_id": oid})

    async def resolve_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        try:
            oid = ObjectId(event_id)
        except Exception:
            return False
        updates["updated_at"] = datetime.now(timezone.utc)
        res = self.get_collection().update_one({"_id": oid}, {"$set": updates})
        return bool(getattr(res, "modified_count", 0))


class SafetyNotesRepository(BaseRepository):
    """Store notes related to safety events."""

    COLLECTION_NAME = "safety_notes"

    async def add_note(self, event_id: str, author: str, content: str, note_type: str = "note") -> str:
        doc = {
            "event_id": event_id,
            "author": author,
            "note_type": note_type,
            "content": content,
            "created_at": datetime.now(timezone.utc),
        }
        result = self.get_collection().insert_one(doc)
        return str(result.inserted_id)

    async def list_for_event(self, event_id: str) -> List[Dict[str, Any]]:
        cursor = self.get_collection().find({"event_id": event_id}).sort("created_at", -1)
        return list(cursor)
