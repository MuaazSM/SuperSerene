"""Chat API routes.

Endpoints:
- POST /api/chat/{session_id} - Send message and get response
- GET /api/sessions - List sessions
- POST /api/sessions - Create session
- PATCH /api/sessions/{session_id} - Update session
- DELETE /api/sessions/{session_id} - Delete session
- POST /api/messages - Add message
- GET /api/messages - Get messages
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from api.deps import get_current_user, get_optional_current_user, get_db, get_orchestrator
from services.chat_service import ChatService
from db.mongo import Collections
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)

router = APIRouter()


def get_chat_service(
    db=Depends(get_db),
    orchestrator=Depends(get_orchestrator),
) -> ChatService:
    """Dependency provider for ChatService."""
    return ChatService(db=db, orchestrator=orchestrator)


@router.post("/sessions/{session_id}/messages", tags=["chat"])
async def send_message(
    session_id: str,
    request: Dict = None,
    current_user: Optional[Dict] = Depends(get_optional_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Send message to chat and get response.
    
    Args:
        session_id: Chat session ID
        request: Message request (content, etc)
        current_user: Current authenticated user
        db: Database connection
        orchestrator: Orchestrator instance
        
    Returns:
        Response with message and analysis
        
    Raises:
        HTTPException: On error
    """
    try:
        if not request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request body required"
            )
        
        user_id = (current_user or {}).get("user_id", "guest")
        message_text = (request.get("content") or request.get("message") or "").strip()
        
        if not message_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content is required"
            )
        
        response = await service.send_message(
            session_id=session_id,
            user_id=user_id,
            content=message_text,
        )

        _LOG.info("Chat message processed", user_id=user_id, session_id=session_id)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        _LOG.error("Chat message processing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.post("/{session_id:^[0-9a-fA-F]{24}$}", tags=["chat"])
async def send_message_legacy(
    session_id: str,
    request: Dict = None,
    current_user: Dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Legacy route for sending a message (compatibility with older clients)."""
    return await send_message(
        session_id=session_id,
        request=request,
        current_user=current_user,
        service=service,
    )


@router.get("/sessions", tags=["chat"])
async def list_sessions(
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: Dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """List chat sessions.
    
    Args:
        user_id: Filter by user (defaults to current user)
        limit: Max sessions to return
        skip: Offset for pagination
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        List of session objects
    """
    try:
        filter_user = user_id or current_user.get("user_id")
        return await service.list_sessions(user_id=filter_user, limit=limit, skip=skip)
    except Exception as e:
        _LOG.error("Failed to list sessions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list sessions"
        )


@router.post("/sessions", tags=["chat"])
async def create_session(
    request: Dict,
    current_user: Optional[Dict] = Depends(get_optional_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Create new chat session.
    
    Args:
        request: Session details (session_name, etc)
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        Created session object
    """
    try:
        session_doc = await service.create_session(
            user_id=(current_user or {}).get("user_id", "guest"),
            session_name=request.get("session_name", "New Chat"),
        )
        session_doc["metadata"] = request.get("metadata", {})
        session_doc["session_id"] = session_doc.get("_id")
        _LOG.info("Session created", user_id=current_user.get("user_id"))
        return session_doc
    except Exception as e:
        _LOG.error("Failed to create session", error=str(e))
        # Provide a graceful fallback so clients can continue
        return {
            "session_id": None,
            "session_name": request.get("session_name") or request.get("title") or "New Chat",
            "metadata": request.get("metadata", {}),
            "error": "session_creation_failed",
        }


@router.patch("/sessions/{session_id}", tags=["chat"])
async def update_session(
    session_id: str,
    request: Dict,
    current_user: Dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Update chat session.
    
    Args:
        session_id: Session ID to update
        request: Fields to update
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        Updated session object
    """
    try:
        updated = await service.update_session(session_id=session_id, updates=request)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        _LOG.info("Session updated", session_id=session_id)
        return {"updated": True}
    except HTTPException:
        raise
    except Exception as e:
        _LOG.error("Failed to update session", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session"
        )


@router.delete("/sessions/{session_id}", tags=["chat"])
async def delete_session(
    session_id: str,
    current_user: Dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Delete chat session.
    
    Args:
        session_id: Session ID to delete
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        Success message
    """
    try:
        deleted = await service.delete_session(session_id=session_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        _LOG.info("Session deleted", session_id=session_id)
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        _LOG.error("Failed to delete session", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


@router.post("/messages", tags=["chat"])
async def add_message(
    request: Dict,
    current_user: Dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Add message to session.
    
    Args:
        request: Message details (session_id, content, etc)
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        Created message object
    """
    try:
        session_id = request.get("session_id")
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id is required"
            )

        message = await service.add_message(
            session_id=session_id,
            user_id=current_user.get("user_id"),
            role=request.get("role", "user"),
            content=request.get("content", ""),
        )
        _LOG.info("Message added", session_id=session_id)
        return message
    except HTTPException:
        raise
    except Exception as e:
        _LOG.error("Failed to add message", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add message"
        )


@router.get("/messages", tags=["chat"])
async def get_messages(
    session_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    current_user: Dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Get messages for a session.
    
    Args:
        session_id: Session ID to get messages from
        limit: Max messages to return
        skip: Offset for pagination
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        List of message objects
    """
    try:
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id is required"
            )

        result = await service.get_messages(
            session_id=session_id,
            user_id=None,
            limit=limit,
            skip=skip,
        )
        return {"messages": result.get("messages", []), "total": result.get("count", 0)}
    except HTTPException:
        raise
    except Exception as e:
        _LOG.error("Failed to get messages", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get messages"
        )
