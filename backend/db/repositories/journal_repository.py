"""Repository for journal-related persistence."""

from datetime import datetime, timezone
from typing import Dict, Any
from bson import ObjectId

from db.repositories.base_repository import BaseRepository


class JournalRepository(BaseRepository):
    """Persist journal entries into messages collection when linked to a session."""

    COLLECTION_NAME = "messages"

    async def create_entry(
        self,
        user_id: str,
        content: str,
        emotion: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Create a standalone journal entry stored in messages collection."""
        doc: Dict[str, Any] = {
            "user_id": user_id,
            "role": "journal",
            "content": content,
            "metadata": {
                "source": "journal",
                "emotion": emotion,
                "tags": tags or [],
            },
            "timestamp": datetime.now(timezone.utc),
        }
        result = self.get_collection().insert_one(doc)
        return str(result.inserted_id)

    async def list_entries(self, user_id: str, limit: int, skip: int) -> list[Dict[str, Any]]:
        cursor = (
            self.get_collection()
            .find({"user_id": user_id, "role": "journal"})
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )
        return list(cursor)

    async def get_entry(self, entry_id: str) -> Dict[str, Any] | None:
        try:
            oid = ObjectId(entry_id)
        except Exception:
            return None
        return self.get_collection().find_one({"_id": oid, "role": "journal"})

    async def update_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        try:
            oid = ObjectId(entry_id)
        except Exception:
            return False
        updates["timestamp"] = datetime.now(timezone.utc)
        res = self.get_collection().update_one({"_id": oid, "role": "journal"}, {"$set": updates})
        return bool(getattr(res, "modified_count", 0))

    async def delete_entry(self, entry_id: str) -> bool:
        try:
            oid = ObjectId(entry_id)
        except Exception:
            return False
        res = self.get_collection().delete_one({"_id": oid, "role": "journal"})
        return bool(getattr(res, "deleted_count", 0))

    async def save_entry_message(
        self,
        session_id: str,
        user_id: str,
        text: str,
        mood: int,
    ) -> str:
        doc: Dict[str, Any] = {
            "session_id": session_id,
            "user_id": user_id,
            "role": "user",
            "content": text,
            "metadata": {
                "source": "journal",
                "mood": mood,
            },
            "timestamp": datetime.now(timezone.utc),
        }
        result = self.get_collection().insert_one(doc)
        return str(result.inserted_id)
