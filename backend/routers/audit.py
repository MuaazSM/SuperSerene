"""
Audit log API — admin-only access to guardian notification audit trail.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query

from api.deps import get_current_user
from services.audit_log import get_audit_trail
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)
router = APIRouter()


@router.get("/user/{user_id}", tags=["audit"])
async def audit_trail(
    user_id: str,
    limit: int = Query(100, ge=1, le=500),
    current_user=Depends(get_current_user),
):
    """
    Retrieve guardian notification audit trail for a user.
    Admin/coordinator only.
    """
    role = current_user.get("role", "individual")
    if role not in ("coordinator", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access audit logs",
        )
    records = get_audit_trail(user_id=user_id, limit=limit)
    return {"user_id": user_id, "records": records, "count": len(records)}
