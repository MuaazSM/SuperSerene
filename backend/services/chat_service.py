"""Chat service handling sessions and messages."""

from typing import Dict, Any, Optional, List

from services.base_service import BaseService
from db.repositories.session_repository import SessionRepository, MessageRepository


class ChatService(BaseService):
    """Service for chat orchestration and session management."""

    async def send_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        mode: str = "qa",
    ) -> Dict[str, Any]:
        if not content:
            raise ValueError("Message content is required")

        messages = MessageRepository(self.db)

        await messages.add_message(session_id=session_id, user_id=user_id, role="user", content=content)

        # Orchestrate reply
        reply = await self.orchestrator.chat(
            user_id=user_id,
            session_id=session_id,
            message=content,
            mode=mode,
        )

        # Persist assistant message (store only the text for readability)
        reply_text = reply.get("text") if isinstance(reply, dict) else str(reply)
        await messages.add_message(session_id=session_id, user_id=user_id, role="assistant", content=reply_text)

        self.log_info("Chat processed", session_id=session_id, user_id=user_id)
        return {"response": reply}

    async def list_sessions(self, user_id: str, limit: int = 50, skip: int = 0) -> Dict[str, Any]:
        repo = SessionRepository(self.db)
        sessions = await repo.list_sessions(user_id=user_id, limit=limit, skip=skip)
        # Ensure IDs are stringified for JSON responses
        serialized = [{**s, "_id": str(s.get("_id"))} for s in sessions]
        return {"sessions": serialized, "total": len(serialized)}

    async def create_session(self, user_id: str, session_name: str = "New Chat") -> Dict[str, Any]:
        repo = SessionRepository(self.db)
        doc = await repo.create_session(user_id=user_id, session_name=session_name)
        doc["_id"] = str(doc.get("_id"))
        return doc

    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        repo = SessionRepository(self.db)
        return await repo.update_session(session_id=session_id, updates=updates)

    async def delete_session(self, session_id: str) -> bool:
        sessions = SessionRepository(self.db)
        messages = MessageRepository(self.db)
        await messages.delete_by_session(session_id=session_id)
        return await sessions.delete_session(session_id=session_id)

    async def add_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
    ) -> Dict[str, Any]:
        if role not in {"user", "assistant"}:
            raise ValueError("role must be 'user' or 'assistant'")
        messages = MessageRepository(self.db)
        msg = await messages.add_message(session_id=session_id, user_id=user_id, role=role, content=content)
        msg["_id"] = str(msg.get("_id"))
        return msg

    async def get_messages(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {}
        if session_id:
            query["session_id"] = session_id
        if user_id:
            query["user_id"] = user_id

        messages_repo = MessageRepository(self.db)
        messages = await messages_repo.list_messages(query=query, limit=limit, skip=skip)
        serialized = [{**m, "_id": str(m.get("_id"))} for m in messages]
        return {"messages": serialized, "count": len(serialized)}
