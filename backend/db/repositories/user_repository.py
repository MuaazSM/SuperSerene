"""Repository for user document operations."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId

from db.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository handling user CRUD and profile updates."""

    COLLECTION_NAME = "users"

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.get_collection().find_one({"email": email})

    async def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:  # type: ignore[override]
        collection = self.get_collection()
        # Try user_id field first (UUID string)
        doc = collection.find_one({"user_id": user_id})
        if doc:
            return doc
        # Fallback to _id (ObjectId)
        try:
            oid = ObjectId(user_id)
            return collection.find_one({"_id": oid})
        except Exception:
            return None

    async def create_user(self, name: str, email: str, hashed_password: str, role: str = "individual") -> Dict[str, Any]:
        from uuid import uuid4
        
        doc = {
            "user_id": str(uuid4()),  # Generate unique user_id
            "email": email,
            "name": name,
            "hashed_password": hashed_password,
            "role": role,
            "created_at": datetime.now(timezone.utc),
            "last_login": datetime.now(timezone.utc),
            "preferences": {},
            "metadata": {},
        }
        result = self.get_collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def update_last_login(self, user_id: str) -> None:
        collection = self.get_collection()
        # Try user_id field first
        res = collection.update_one({"user_id": user_id}, {"$set": {"last_login": datetime.now(timezone.utc)}})
        if res.modified_count > 0:
            return
        # Fallback to _id
        try:
            oid = ObjectId(user_id)
            collection.update_one({"_id": oid}, {"$set": {"last_login": datetime.now(timezone.utc)}})
        except Exception:
            pass

    async def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        allowed_fields = {"name", "bio", "strengths", "focus", "preferences", "metadata"}
        filtered = {k: v for k, v in updates.items() if k in allowed_fields}
        if not filtered:
            return False
        filtered["updated_at"] = datetime.now(timezone.utc)
        collection = self.get_collection()
        # Try user_id field first
        res = collection.update_one({"user_id": user_id}, {"$set": filtered})
        if res.modified_count > 0:
            return True
        # Fallback to _id
        try:
            oid = ObjectId(user_id)
            res = collection.update_one({"_id": oid}, {"$set": filtered})
            return bool(getattr(res, "modified_count", 0))
        except Exception:
            return False
