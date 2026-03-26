"""
Guardian notification service.

Manages guardian registration, verification, and privacy-safe notifications
for users under 16.  Notifications NEVER include message/journal content —
only severity level, timestamp, and a generic recommended action.
"""

import os
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from db.mongo import get_mongo
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)


# ---------------------------------------------------------------------------
# SMTP helpers (configurable via env)
# ---------------------------------------------------------------------------

def _smtp_config() -> Dict[str, Any]:
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from_addr": os.getenv("SMTP_FROM", os.getenv("SMTP_USER", "noreply@superserene.app")),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
    }


def _send_email(to_addr: str, subject: str, html_body: str) -> bool:
    """Send email via SMTP.  Returns True on success."""
    cfg = _smtp_config()
    if not cfg["user"] or not cfg["password"]:
        _LOG.warning("SMTP not configured — email not sent", to=to_addr)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = cfg["from_addr"]
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as server:
            if cfg["use_tls"]:
                server.starttls()
            server.login(cfg["user"], cfg["password"])
            server.sendmail(cfg["from_addr"], [to_addr], msg.as_string())
        _LOG.info("Email sent", to=to_addr, subject=subject)
        return True
    except Exception as e:
        _LOG.error("Email delivery failed", to=to_addr, error=str(e))
        return False


# ---------------------------------------------------------------------------
# Guardian CRUD
# ---------------------------------------------------------------------------

def register_guardian(
    user_id: str,
    guardian_email: str,
    guardian_name: str,
    relationship: str = "parent",
) -> Dict[str, Any]:
    """Register a guardian for a user and send verification email."""
    mongo = get_mongo()
    token = uuid.uuid4().hex

    doc = {
        "user_id": user_id,
        "guardian_name": guardian_name,
        "guardian_email": guardian_email,
        "relationship": relationship,
        "verified": False,
        "verification_token": token,
        "created_at": datetime.now(timezone.utc),
    }

    # Upsert: one guardian per user
    mongo.db.guardians.update_one(
        {"user_id": user_id},
        {"$set": doc},
        upsert=True,
    )
    _LOG.info("Guardian registered", user_id=user_id, email=guardian_email)

    # Send verification email
    frontend = os.getenv("FRONTEND_URL", "http://localhost:3000")
    backend = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
    verify_link = f"{backend}/api/v1/guardian/verify/{token}"

    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;padding:24px;">
        <h2 style="color:#1a1a2e;">SuperSerene — Guardian Verification</h2>
        <p>Hi {guardian_name},</p>
        <p>Someone has listed you as their guardian on SuperSerene, a youth mental wellness platform.</p>
        <p>If you agree to receive <strong>safety-only</strong> notifications when our system
        detects the young person may need urgent support, please click below to verify:</p>
        <p style="text-align:center;margin:24px 0;">
            <a href="{verify_link}"
               style="background:#4f46e5;color:#fff;padding:12px 28px;border-radius:8px;
                      text-decoration:none;font-weight:600;">
                Verify Guardian Link
            </a>
        </p>
        <p style="font-size:13px;color:#666;">
            You will <strong>never</strong> receive the young person's private messages or journal
            entries — only the severity level and a recommended action.
        </p>
        <p style="font-size:12px;color:#999;">
            If you did not expect this email, you can safely ignore it.
        </p>
    </div>
    """
    _send_email(guardian_email, "SuperSerene — Verify your guardian link", html)

    return {"user_id": user_id, "guardian_email": guardian_email, "verification_token": token}


def verify_guardian(token: str) -> bool:
    """Mark guardian as verified.  Returns True if found and updated."""
    mongo = get_mongo()
    result = mongo.db.guardians.update_one(
        {"verification_token": token, "verified": False},
        {"$set": {"verified": True, "verified_at": datetime.now(timezone.utc)}},
    )
    if result.modified_count > 0:
        _LOG.info("Guardian verified", token=token[:8])
        return True
    _LOG.warning("Guardian verification failed — token not found or already verified", token=token[:8])
    return False


def get_guardian(user_id: str) -> Optional[Dict[str, Any]]:
    """Return guardian record for a user, or None."""
    mongo = get_mongo()
    return mongo.db.guardians.find_one({"user_id": user_id}, {"_id": 0})


def remove_guardian(user_id: str) -> bool:
    """Remove the guardian link for a user."""
    mongo = get_mongo()
    result = mongo.db.guardians.delete_one({"user_id": user_id})
    return result.deleted_count > 0


# ---------------------------------------------------------------------------
# Notification logic
# ---------------------------------------------------------------------------

def _get_user_age(user_id: str) -> Optional[int]:
    """Return the user's age if stored, else None."""
    mongo = get_mongo()
    user = mongo.get_user(user_id) or mongo.db.users.find_one({"user_id": user_id})
    if not user:
        return None
    dob = user.get("date_of_birth") or user.get("dob")
    age = user.get("age")
    if age is not None:
        return int(age)
    if dob:
        today = datetime.now(timezone.utc).date()
        if isinstance(dob, str):
            dob = datetime.fromisoformat(dob).date()
        elif isinstance(dob, datetime):
            dob = dob.date()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return None


def should_notify(user_id: str, risk_band: str) -> bool:
    """
    Returns True when ALL conditions are met:
    1. risk_band is "orange" or "red"
    2. user is under 16
    3. user has a verified guardian
    """
    if risk_band not in ("orange", "red"):
        return False

    age = _get_user_age(user_id)
    if age is None or age >= 16:
        return False

    guardian = get_guardian(user_id)
    if not guardian or not guardian.get("verified"):
        return False

    return True


def send_notification(
    user_id: str,
    event_type: str,
    severity: str,
    summary: str,
) -> bool:
    """
    Send a privacy-safe notification to the guardian.

    The email NEVER contains user messages or journal content — only:
    - What triggered it (crisis detection / screening result)
    - Severity level
    - Recommended action
    - Crisis resource links
    """
    guardian = get_guardian(user_id)
    if not guardian or not guardian.get("verified"):
        _LOG.warning("Cannot notify — no verified guardian", user_id=user_id)
        return False

    guardian_name = guardian.get("guardian_name", "Guardian")
    guardian_email = guardian["guardian_email"]
    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

    # Map severity to recommendation
    if severity in ("red", "severe", "moderately_severe"):
        action = "We recommend speaking with your child soon and considering a conversation with a mental health professional."
        urgency = "High"
    elif severity in ("orange", "moderate", "positive"):
        action = "Your child may benefit from speaking with a counselor. No immediate danger detected."
        urgency = "Moderate"
    else:
        action = "Continued monitoring recommended."
        urgency = "Low"

    html = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:auto;padding:24px;">
        <h2 style="color:#1a1a2e;">SuperSerene — Guardian Alert</h2>
        <p>Hi {guardian_name},</p>
        <p>Our system has detected a situation that warrants your awareness.</p>

        <table style="width:100%;border-collapse:collapse;margin:16px 0;">
            <tr><td style="padding:8px;font-weight:600;color:#555;">Triggered by</td>
                <td style="padding:8px;">{event_type}</td></tr>
            <tr style="background:#f9f9fb;">
                <td style="padding:8px;font-weight:600;color:#555;">Urgency</td>
                <td style="padding:8px;">{urgency}</td></tr>
            <tr><td style="padding:8px;font-weight:600;color:#555;">Severity</td>
                <td style="padding:8px;">{severity}</td></tr>
            <tr style="background:#f9f9fb;">
                <td style="padding:8px;font-weight:600;color:#555;">Timestamp</td>
                <td style="padding:8px;">{now}</td></tr>
        </table>

        <p><strong>Recommended action:</strong> {action}</p>

        <h3 style="margin-top:24px;">Crisis Resources</h3>
        <ul style="padding-left:18px;color:#444;">
            <li><strong>988 Suicide &amp; Crisis Lifeline</strong> — Call or text <strong>988</strong></li>
            <li><strong>Crisis Text Line</strong> — Text HOME to <strong>741741</strong></li>
            <li><strong>AASRA (India)</strong> — <strong>91-9820466726</strong></li>
        </ul>

        <p style="font-size:13px;color:#666;margin-top:20px;">
            <em>For your child's privacy, this notification does not include any messages,
            journal entries, or specific content. Only the severity level and a general
            recommended action are shared.</em>
        </p>
    </div>
    """

    sent = _send_email(guardian_email, f"SuperSerene Alert — {urgency} urgency notification", html)

    # Always create audit record
    from services.audit_log import create_audit_record
    create_audit_record(
        user_id=user_id,
        event_type=event_type,
        severity=severity,
        notification_sent=sent,
        guardian_id=guardian.get("guardian_email", ""),
        summary_sent=f"Urgency: {urgency}. Action: {action}",
        triggered_by=event_type,
    )

    return sent
