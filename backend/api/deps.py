"""Shared dependencies for FastAPI routes.

This module provides dependency injection for:
- Authentication (get_current_user)
- Database access (get_db)
- Business logic (get_orchestrator, get_services)
"""

from typing import Optional, Dict, Any, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth import verify_jwt_token
from db.mongo import get_mongo, Collections
from core.orchestrator import Orchestrator
from config import settings
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)


security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[Collections, None]:
    """Get database connection.
    
    Returns:
        Collections: MongoDB collections context manager.
        
    Raises:
        HTTPException: If database connection fails.
    """
    db = get_mongo()
    yield db


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token from Authorization header.
        
    Returns:
        Dict: Decoded JWT payload containing user info.
        
    Raises:
        HTTPException: If token is invalid or expired (401).
    """
    token = credentials.credentials
    
    try:
        payload = verify_jwt_token(token)
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except Exception as e:
        _LOG.warning("Token verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, otherwise return None.
    
    Useful for endpoints that work with or without auth.
    
    Args:
        credentials: Optional HTTP Bearer token.
        
    Returns:
        Dict: Decoded JWT payload if authenticated, None otherwise.
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def ensure_role(*allowed_roles: str):
    """Factory to create role-based access control dependency.
    
    Args:
        allowed_roles: List of roles that are allowed to access endpoint.
        
    Returns:
        Callable: Dependency that checks user role.
        
    Example:
        @router.post("/admin/settings")
        async def admin_settings(
            current_user: Dict = Depends(get_current_user),
            _: None = Depends(ensure_role("admin", "coordinator"))
        ):
            pass
    """
    async def check_role(current_user: Dict = Depends(get_current_user)) -> None:
        user_role = current_user.get("role", "user")
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This endpoint requires one of: {', '.join(allowed_roles)}"
            )
    
    return check_role


# Service dependencies (lazy-loaded to avoid circular imports)

_orchestrator_instance: Optional[Orchestrator] = None


async def get_orchestrator() -> Orchestrator:
    """Get or create orchestrator instance.
    
    Returns:
        Orchestrator: Agent orchestration system.
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance
