"""Repository for chat sessions and messages."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from bson import ObjectId

from db.repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository):
    """Manage chat sessions."""

    COLLECTION_NAME = "sessions"

    async def create_session(self, user_id: str, session_name: str) -> Dict[str, Any]:
        doc = {
            "user_id": user_id,
            "session_name": session_name,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_pinned": False,
            "message_count": 0,
            "metadata": {},
        }
        result = self.get_collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def find_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            collection = self.get_collection()
            # Sessions use string session_id, not ObjectId _id
            doc = collection.find_one({"session_id": session_id})
            if doc:
                return doc
            # Fallback to _id for backward compatibility
            try:
                return collection.find_one({"_id": ObjectId(session_id)})
            except Exception:
                return None
        except Exception as e:
            self._logger.error(f"Error finding session: {session_id}", error=str(e))
            return None

    async def list_sessions(self, user_id: str, limit: int, skip: int) -> List[Dict[str, Any]]:
        cursor = self.get_collection().find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        return list(cursor)

    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        updates["updated_at"] = datetime.now(timezone.utc)
        # Try session_id field first
        res = self.get_collection().update_one({"session_id": session_id}, {"$set": updates})
        if res.modified_count > 0:
            return True
        # Fallback to _id
        try:
            oid = ObjectId(session_id)
            res = self.get_collection().update_one({"_id": oid}, {"$set": updates})
            return bool(getattr(res, "modified_count", 0))
        except Exception:
            return False

    async def delete_session(self, session_id: str) -> bool:
        # Try session_id field first
        res = self.get_collection().delete_one({"session_id": session_id})
        if res.deleted_count > 0:
            return True
        # Fallback to _id
        try:
            oid = ObjectId(session_id)
            res = self.get_collection().delete_one({"_id": oid})
            return bool(getattr(res, "deleted_count", 0))
        except Exception:
            return False


class MessageRepository(BaseRepository):
    """Manage chat messages."""

    COLLECTION_NAME = "messages"

    async def add_message(self, session_id: str, user_id: str, role: str, content: str) -> Dict[str, Any]:
        msg = {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc),
        }
        result = self.get_collection().insert_one(msg)
        msg["_id"] = result.inserted_id
        return msg

    async def list_messages(self, query: Dict[str, Any], limit: int, skip: int) -> List[Dict[str, Any]]:
        cursor = (
            self.get_collection()
            .find(query)
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )
        return list(cursor)

    async def delete_by_session(self, session_id: str) -> int:
        res = self.get_collection().delete_many({"session_id": session_id})
        return int(getattr(res, "deleted_count", 0))
