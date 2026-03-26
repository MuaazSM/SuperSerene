"""
Tests for guardian notification service — privacy and logic tests.

These tests verify the notification logic WITHOUT requiring a database
connection. They test the should_notify decision logic and email template
safety (no message content leaked).
"""

import pytest
from unittest.mock import patch, MagicMock
from services.guardian_service import (
    should_notify,
    _smtp_config,
)


class TestShouldNotify:
    """Test the should_notify decision logic."""

    @patch("services.guardian_service._get_user_age", return_value=14)
    @patch("services.guardian_service.get_guardian", return_value={"verified": True, "guardian_email": "parent@test.com"})
    def test_notifies_for_minor_with_red_band(self, mock_guardian, mock_age):
        assert should_notify("user_123", "red") is True

    @patch("services.guardian_service._get_user_age", return_value=14)
    @patch("services.guardian_service.get_guardian", return_value={"verified": True, "guardian_email": "parent@test.com"})
    def test_notifies_for_minor_with_orange_band(self, mock_guardian, mock_age):
        assert should_notify("user_123", "orange") is True

    @patch("services.guardian_service._get_user_age", return_value=14)
    @patch("services.guardian_service.get_guardian", return_value={"verified": True})
    def test_no_notify_for_green_band(self, mock_guardian, mock_age):
        assert should_notify("user_123", "green") is False

    @patch("services.guardian_service._get_user_age", return_value=14)
    @patch("services.guardian_service.get_guardian", return_value={"verified": True})
    def test_no_notify_for_yellow_band(self, mock_guardian, mock_age):
        assert should_notify("user_123", "yellow") is False

    @patch("services.guardian_service._get_user_age", return_value=17)
    @patch("services.guardian_service.get_guardian", return_value={"verified": True})
    def test_no_notify_for_adult(self, mock_guardian, mock_age):
        assert should_notify("user_123", "red") is False

    @patch("services.guardian_service._get_user_age", return_value=14)
    @patch("services.guardian_service.get_guardian", return_value={"verified": False})
    def test_no_notify_unverified_guardian(self, mock_guardian, mock_age):
        assert should_notify("user_123", "red") is False

    @patch("services.guardian_service._get_user_age", return_value=14)
    @patch("services.guardian_service.get_guardian", return_value=None)
    def test_no_notify_no_guardian(self, mock_guardian, mock_age):
        assert should_notify("user_123", "red") is False

    @patch("services.guardian_service._get_user_age", return_value=None)
    @patch("services.guardian_service.get_guardian", return_value={"verified": True})
    def test_no_notify_unknown_age(self, mock_guardian, mock_age):
        assert should_notify("user_123", "red") is False

    @patch("services.guardian_service._get_user_age", return_value=15)
    @patch("services.guardian_service.get_guardian", return_value={"verified": True})
    def test_notifies_for_age_15(self, mock_guardian, mock_age):
        """15 is under 16 — should notify."""
        assert should_notify("user_123", "red") is True

    @patch("services.guardian_service._get_user_age", return_value=16)
    @patch("services.guardian_service.get_guardian", return_value={"verified": True})
    def test_no_notify_for_age_16(self, mock_guardian, mock_age):
        """16 is NOT under 16 — should not notify."""
        assert should_notify("user_123", "red") is False


class TestSMTPConfig:
    def test_config_returns_dict(self):
        cfg = _smtp_config()
        assert isinstance(cfg, dict)
        assert "host" in cfg
        assert "port" in cfg
        assert "user" in cfg
        assert "password" in cfg

    def test_default_host(self):
        cfg = _smtp_config()
        assert cfg["host"] == "smtp.gmail.com"

    def test_default_port(self):
        cfg = _smtp_config()
        assert cfg["port"] == 587


class TestNotificationPrivacy:
    """Verify that notification emails never contain user message content."""

    @patch("services.guardian_service.get_guardian", return_value={"verified": True, "guardian_email": "parent@test.com", "guardian_name": "Parent"})
    @patch("services.guardian_service._send_email", return_value=True)
    @patch("services.audit_log.create_audit_record", return_value="audit_123")
    def test_notification_does_not_contain_user_messages(self, mock_audit, mock_email, mock_guardian):
        from services.guardian_service import send_notification

        secret_message = "I told my friend a secret about my crush at school"
        send_notification(
            user_id="user_123",
            event_type="chat_crisis_detection",
            severity="red",
            summary=secret_message,  # This should NOT appear in the email
        )

        # Check the email was called
        mock_email.assert_called_once()
        email_html = mock_email.call_args[0][2]  # Third arg is html_body

        # The user's actual message should NOT be in the email
        assert secret_message not in email_html
        assert "crush" not in email_html
        assert "friend" not in email_html

        # But severity and recommended action SHOULD be present
        assert "High" in email_html or "Moderate" in email_html or "red" in email_html
        assert "Guardian Alert" in mock_email.call_args[0][1]  # Subject
