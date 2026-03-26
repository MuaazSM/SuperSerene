"""
Immutable audit log for guardian notifications.

Every guardian notification creates a record that cannot be modified or deleted
through the application.  Admin-only retrieval endpoint.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from db.mongo import get_mongo
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)


def _ensure_indexes():
    """Create audit_log indexes (idempotent)."""
    try:
        mongo = get_mongo()
        coll = mongo.db.audit_log
        coll.create_index([("user_id", 1), ("timestamp", -1)], name="user_audit_by_date")
        coll.create_index("timestamp", name="audit_timestamp_idx")
    except Exception:
        pass


def create_audit_record(
    user_id: str,
    event_type: str,
    severity: str,
    notification_sent: bool,
    guardian_id: str,
    summary_sent: str,
    triggered_by: str,
) -> str:
    """
    Create an immutable audit record.

    Returns the inserted document's string _id.
    """
    _ensure_indexes()
    mongo = get_mongo()

    doc = {
        "user_id": user_id,
        "event_type": event_type,
        "severity": severity,
        "notification_sent": notification_sent,
        "guardian_id": guardian_id,
        "summary_sent": summary_sent,
        "triggered_by": triggered_by,
        "timestamp": datetime.now(timezone.utc),
    }

    result = mongo.db.audit_log.insert_one(doc)
    _LOG.info(
        "Audit record created",
        user_id=user_id,
        event_type=event_type,
        severity=severity,
        notification_sent=notification_sent,
    )
    return str(result.inserted_id)


def get_audit_trail(
    user_id: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Return audit records for a user, newest first."""
    mongo = get_mongo()
    cursor = mongo.db.audit_log.find(
        {"user_id": user_id},
        {"_id": 0},
    ).sort("timestamp", -1).limit(limit)
    return list(cursor)
