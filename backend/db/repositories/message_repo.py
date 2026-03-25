"""Message Repository for storing and retrieving messages."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

from logger.custom_logger import CustomLogger
from db.repositories.base_repository import BaseRepository

_LOG = CustomLogger().get_logger(__name__)


class MessageType(str, Enum):
    """Message type enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message:
    """Simple Message model."""
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        content: str,
        message_type: MessageType,
        is_voice: bool = False,
        sentiment: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.content = content
        self.message_type = message_type
        self.is_voice = is_voice
        self.sentiment = sentiment
        self.timestamp = timestamp or datetime.utcnow()


class MessageRepository(BaseRepository):
    """Repository for Message operations."""
    
    def __init__(self, db):
        """Initialize with database instance."""
        super().__init__(db, "messages")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for efficient queries."""
        try:
            self.collection.create_index([("session_id", 1)])
            self.collection.create_index([("user_id", 1)])
            self.collection.create_index([("timestamp", -1)])
            self.collection.create_index([("session_id", 1), ("timestamp", -1)])
        except Exception as e:
            _LOG.warning(f"Failed to create indexes: {e}")
    
    async def create(self, message: Message) -> str:
        """
        Create a new message.
        
        Args:
            message: Message object to store
            
        Returns:
            Message ID
        """
        doc = {
            "session_id": message.session_id,
            "user_id": message.user_id,
            "content": message.content,
            "message_type": message.message_type.value if hasattr(message.message_type, 'value') else str(message.message_type),
            "is_voice": message.is_voice,
            "sentiment": message.sentiment,
            "timestamp": message.timestamp
        }
        
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a session."""
        try:
            session_oid = ObjectId(session_id) if isinstance(session_id, str) else session_id
            cursor = self.collection.find({"session_id": session_oid}).sort("timestamp", 1)
            return [doc async for doc in cursor]
        except Exception as e:
            _LOG.error(f"Failed to get messages: {e}")
            return []
    
    async def get_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all messages by a user."""
        try:
            user_oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
            cursor = self.collection.find({"user_id": user_oid}).sort("timestamp", -1)
            return [doc async for doc in cursor]
        except Exception as e:
            _LOG.error(f"Failed to get user messages: {e}")
            return []
