"""Safety and crisis management service."""

from typing import Dict, Any, Optional

from services.base_service import BaseService
from db.repositories.safety_repository import SafetyRepository, SafetyNotesRepository


class SafetyService(BaseService):
    """Service for safety events and alerts."""

    async def create_event(
        self,
        user_id: str,
        description: str,
        severity: int,
        immediate_risk: bool,
    ) -> Dict[str, Any]:
        if not description:
            raise ValueError("Description required")
        if not 1 <= severity <= 5:
            raise ValueError("Severity must be 1-5")

        try:
            events = SafetyRepository(self.db)
            event = {
                "user_id": user_id,
                "description": description,
                "severity": severity,
                "immediate_risk": immediate_risk,
            }
            event_id = await events.create_event(event)

            if severity >= 4 or immediate_risk:
                try:
                    await self.orchestrator.escalate_crisis(
                        user_id=user_id,
                        event_id=event_id,
                        severity=severity,
                        description=description,
                    )
                except Exception as e:
                    self.log_warning("Safety escalation failed", error=str(e))
            return {"id": event_id, "status": "open", "severity": severity}
        except Exception as e:
            self.log_warning("Safety event creation failed", error=str(e))
            return {"id": None, "status": "open", "severity": severity, "error": "safety_unavailable"}

    async def list_events(self, user_id: str, status: Optional[str], limit: int, skip: int) -> Dict[str, Any]:
        events_repo = SafetyRepository(self.db)
        events = await events_repo.list_events(user_id=user_id, status=status, limit=limit, skip=skip)
        serialized = [{**e, "_id": str(e.get("_id"))} for e in events]
        return {"events": serialized, "count": len(serialized)}

    async def get_event(self, event_id: str, requester_id: str, role: str) -> Dict[str, Any]:
        events_repo = SafetyRepository(self.db)
        notes_repo = SafetyNotesRepository(self.db)

        event = await events_repo.get_event(event_id)
        if not event:
            raise ValueError("Event not found")

        if event.get("user_id") != requester_id and role != "admin":
            raise PermissionError("Not authorized to view this event")

        notes = await notes_repo.list_for_event(event_id)
        serialized_notes = [{**n, "_id": str(n.get("_id"))} for n in notes]
        event["_id"] = str(event.get("_id"))
        return {"event": event, "notes": serialized_notes, "note_count": len(serialized_notes)}

    async def resolve_event(
        self,
        event_id: str,
        requester_id: str,
        role: str,
        outcome: str,
        notes: str,
        follow_up_needed: bool,
    ) -> Dict[str, Any]:
        events_repo = SafetyRepository(self.db)
        notes_repo = SafetyNotesRepository(self.db)

        event = await events_repo.get_event(event_id)
        if not event:
            raise ValueError("Event not found")
        if event.get("user_id") != requester_id and role != "admin":
            raise PermissionError("Not authorized to resolve this event")

        await events_repo.resolve_event(
            event_id=event_id,
            updates={
                "status": "resolved",
                "outcome": outcome,
                "follow_up_needed": follow_up_needed,
                "resolved_by": requester_id,
            },
        )

        if notes:
            await notes_repo.add_note(
                event_id=event_id,
                author=requester_id,
                content=notes,
                note_type="resolution",
            )

        return {
            "id": event_id,
            "status": "resolved",
            "outcome": outcome,
            "follow_up_needed": follow_up_needed,
        }

    async def test_alert(self, user_id: str, severity: int) -> Dict[str, Any]:
        return await self.orchestrator.send_test_alert(
            user_id=user_id,
            severity=severity,
            message=f"Test alert at severity {severity}",
        )

