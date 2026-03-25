"""Journal analysis service."""

from typing import Dict, Any
from datetime import datetime, timezone

from services.base_service import BaseService
from db.repositories.journal_repository import JournalRepository


class JournalService(BaseService):
    """Service for journal-related operations."""

    async def create_entry(self, user_id: str, content: str, emotion: str | None, tags: list[str] | None) -> Dict[str, Any]:
        if not content:
            raise ValueError("Content is required")

        repo = JournalRepository(self.db)
        entry_id = await repo.create_entry(user_id=user_id, content=content, emotion=emotion, tags=tags)
        return {"entry_id": entry_id}

    async def list_entries(self, user_id: str, limit: int, skip: int) -> Dict[str, Any]:
        repo = JournalRepository(self.db)
        entries = await repo.list_entries(user_id=user_id, limit=limit, skip=skip)
        serialized = [{**e, "_id": str(e.get("_id"))} for e in entries]
        return {"entries": serialized, "count": len(serialized)}

    async def get_entry(self, entry_id: str) -> Dict[str, Any]:
        repo = JournalRepository(self.db)
        entry = await repo.get_entry(entry_id)
        if not entry:
            raise ValueError("Entry not found")
        entry["_id"] = str(entry.get("_id"))
        return entry

    async def update_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        repo = JournalRepository(self.db)
        return await repo.update_entry(entry_id, updates)

    async def delete_entry(self, entry_id: str) -> bool:
        repo = JournalRepository(self.db)
        return await repo.delete_entry(entry_id)

    async def analyze_journal_entry(
        self,
        user_id: str,
        text: str,
        mood: int = 3,
        session_id: str | None = None,
    ) -> Dict[str, Any]:
        """Analyze a journal entry using the orchestrator and persist metadata."""
        if not text:
            raise ValueError("Journal text is required")

        analysis = await self.orchestrator.process_entry(
            user_id=user_id or "anonymous",
            text=text,
            mood=mood,
        )

        # Persist minimal message record when session provided
        if session_id:
            try:
                repo = JournalRepository(self.db)
                await repo.save_entry_message(
                    session_id=session_id,
                    user_id=user_id,
                    text=text,
                    mood=mood,
                )
            except Exception:
                self.log_warning("Could not persist journal entry", session_id=session_id)

        self.log_info("Journal analyzed", user_id=user_id, session_id=session_id)
        return analysis
