"""
Tests for the audit log service.

Verifies that audit records are created with all required fields
and that the create function accepts the expected parameters.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestAuditLogInterface:
    """Test the audit log function signatures and data structure."""

    @patch("services.audit_log.get_mongo")
    def test_create_record_returns_string(self, mock_mongo):
        mock_coll = MagicMock()
        mock_coll.insert_one.return_value = MagicMock(inserted_id="abc123")
        mock_mongo.return_value.db.audit_log = mock_coll
        mock_mongo.return_value.db.audit_log.create_index = MagicMock()

        from services.audit_log import create_audit_record
        result = create_audit_record(
            user_id="user_123",
            event_type="chat_crisis_detection",
            severity="red",
            notification_sent=True,
            guardian_id="parent@test.com",
            summary_sent="Urgency: High. Action: Speak with child.",
            triggered_by="chat_crisis_detection",
        )
        assert isinstance(result, str)

    @patch("services.audit_log.get_mongo")
    def test_create_record_inserts_correct_fields(self, mock_mongo):
        mock_coll = MagicMock()
        mock_coll.insert_one.return_value = MagicMock(inserted_id="abc123")
        mock_mongo.return_value.db.audit_log = mock_coll
        mock_mongo.return_value.db.audit_log.create_index = MagicMock()

        from services.audit_log import create_audit_record
        create_audit_record(
            user_id="user_123",
            event_type="screening_result",
            severity="orange",
            notification_sent=False,
            guardian_id="",
            summary_sent="Moderate urgency.",
            triggered_by="screening",
        )

        mock_coll.insert_one.assert_called_once()
        doc = mock_coll.insert_one.call_args[0][0]
        assert doc["user_id"] == "user_123"
        assert doc["event_type"] == "screening_result"
        assert doc["severity"] == "orange"
        assert doc["notification_sent"] is False
        assert doc["triggered_by"] == "screening"
        assert "timestamp" in doc
        assert isinstance(doc["timestamp"], datetime)

    @patch("services.audit_log.get_mongo")
    def test_get_audit_trail_returns_list(self, mock_mongo):
        mock_coll = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [{"event_type": "test"}]
        mock_coll.find.return_value = mock_cursor
        mock_mongo.return_value.db.audit_log = mock_coll

        from services.audit_log import get_audit_trail
        result = get_audit_trail("user_123", limit=10)
        assert isinstance(result, list)
