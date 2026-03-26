"""
Guardian management API endpoints.

- POST   /register      — register a guardian (requires user auth)
- GET    /verify/{token} — guardian clicks email link to verify
- GET    /status         — check if current user has a verified guardian
- DELETE /                — remove guardian link
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

from api.deps import get_current_user
from services.guardian_service import (
    register_guardian,
    verify_guardian,
    get_guardian,
    remove_guardian,
)
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)
router = APIRouter()


class RegisterGuardianRequest(BaseModel):
    guardian_email: str
    guardian_name: str
    relationship: str = "parent"


@router.post("/register", tags=["guardian"])
async def register(
    body: RegisterGuardianRequest,
    user=Depends(get_current_user),
):
    """Register a guardian for the current user and send verification email."""
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID not found")

    try:
        result = register_guardian(
            user_id=user_id,
            guardian_email=body.guardian_email,
            guardian_name=body.guardian_name,
            relationship=body.relationship,
        )
        return {"ok": True, "guardian_email": result["guardian_email"]}
    except Exception as e:
        _LOG.error("Guardian registration failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register guardian")


@router.get("/verify/{token}", tags=["guardian"])
async def verify(token: str):
    """Guardian clicks this link from their email to confirm the relationship."""
    success = verify_guardian(token)
    if success:
        html = """
        <html><body style="font-family:sans-serif;text-align:center;padding:60px;">
        <h1 style="color:#16a34a;">Verified!</h1>
        <p>You are now a verified guardian on SuperSerene.</p>
        <p>You will only be contacted if our system detects the young person may need urgent help.</p>
        <p style="color:#888;font-size:13px;">You may close this page.</p>
        </body></html>
        """
        return HTMLResponse(content=html)
    html = """
    <html><body style="font-family:sans-serif;text-align:center;padding:60px;">
    <h1 style="color:#dc2626;">Verification Failed</h1>
    <p>This link may have expired or already been used.</p>
    </body></html>
    """
    return HTMLResponse(content=html, status_code=400)


@router.get("/status", tags=["guardian"])
async def guardian_status(user=Depends(get_current_user)):
    """Check if the current user has a verified guardian."""
    user_id = user.get("user_id")
    guardian = get_guardian(user_id) if user_id else None
    if not guardian:
        return {"has_guardian": False, "verified": False, "guardian_email": None}
    return {
        "has_guardian": True,
        "verified": guardian.get("verified", False),
        "guardian_email": guardian.get("guardian_email"),
        "guardian_name": guardian.get("guardian_name"),
        "relationship": guardian.get("relationship"),
    }


@router.delete("/", tags=["guardian"])
async def delete_guardian(user=Depends(get_current_user)):
    """Remove the guardian link for the current user."""
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID not found")
    removed = remove_guardian(user_id)
    if removed:
        return {"ok": True, "message": "Guardian link removed"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No guardian found")
