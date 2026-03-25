"""Journal API routes.

Endpoints:
- POST /analyze-entry - Analyze journal entry
- POST /analyze-entry-upload - Analyze journal with file upload
"""

import json
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timezone

from logger.custom_logger import CustomLogger
from api.deps import get_db, get_orchestrator, get_current_user
from services.journal_service import JournalService

_LOG = CustomLogger().get_logger(__name__)

router = APIRouter()


def get_journal_service(
    db=Depends(get_db),
    orchestrator=Depends(get_orchestrator),
) -> JournalService:
    """Dependency provider for JournalService."""
    return JournalService(db=db, orchestrator=orchestrator)


@router.post("/analyze-entry", tags=["journal"])
async def analyze_entry(
    request: Request,
    service: JournalService = Depends(get_journal_service),
):
    """Analyze journal entry for emotional content.
    
    Args:
        request: JSON with journal text, user_id, session_id
        
    Returns:
        Analysis with emotions, sentiment, insights, recommendations
        
    Raises:
        HTTPException: On validation or processing error
    """
    try:
        data = await request.json()
        text = (data.get("journal") or data.get("content") or "").strip()
        user_id = data.get("user_id")
        session_id = data.get("session_id")
        
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Journal text is required"
            )
        
        analysis = await service.analyze_journal_entry(
            user_id=user_id or "anonymous",
            text=text,
            mood=data.get("mood", 3),
            session_id=session_id,
        )

        _LOG.info("Journal entry analyzed", user_id=user_id)
        return analysis

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        _LOG.error("Journal analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed"
        )


# CRUD endpoints


@router.post("/", tags=["journal"])
async def create_entry(
    payload: dict,
    service: JournalService = Depends(get_journal_service),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = await service.create_entry(
            user_id=current_user.get("user_id"),
            content=payload.get("content", ""),
            emotion=payload.get("emotion"),
            tags=payload.get("tags", []),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _LOG.error("Failed to create journal entry", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create entry")


@router.get("/", tags=["journal"])
async def list_entries(
    limit: int = Query(20, ge=1, le=200),
    skip: int = Query(0, ge=0),
    service: JournalService = Depends(get_journal_service),
    current_user: dict = Depends(get_current_user),
):
    try:
        return await service.list_entries(user_id=current_user.get("user_id"), limit=limit, skip=skip)
    except Exception as e:
        _LOG.error("Failed to list journal entries", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list entries")


@router.get("/{entry_id}", tags=["journal"])
async def get_entry(
    entry_id: str,
    service: JournalService = Depends(get_journal_service),
    current_user: dict = Depends(get_current_user),
):
    try:
        entry = await service.get_entry(entry_id)
        if entry.get("user_id") != current_user.get("user_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your entry")
        return entry
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        _LOG.error("Failed to get journal entry", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get entry")


@router.put("/{entry_id}", tags=["journal"])
async def update_entry(
    entry_id: str,
    payload: dict,
    service: JournalService = Depends(get_journal_service),
    current_user: dict = Depends(get_current_user),
):
    try:
        # ensure entry exists and belongs to user
        entry = await service.get_entry(entry_id)
        if entry.get("user_id") != current_user.get("user_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your entry")

        updated = await service.update_entry(entry_id, {"content": payload.get("content"), "metadata.emotion": payload.get("emotion"), "metadata.tags": payload.get("tags")})
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
        return {"updated": True}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        _LOG.error("Failed to update journal entry", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update entry")


@router.delete("/{entry_id}", tags=["journal"])
async def delete_entry(
    entry_id: str,
    service: JournalService = Depends(get_journal_service),
    current_user: dict = Depends(get_current_user),
):
    try:
        entry = await service.get_entry(entry_id)
        if entry.get("user_id") != current_user.get("user_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your entry")
        deleted = await service.delete_entry(entry_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
        return {"deleted": True}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        _LOG.error("Failed to delete journal entry", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete entry")


@router.post("/analyze-entry-upload", tags=["journal"])
async def analyze_entry_upload(
    text: Optional[str] = Form(default=""),
    user_id: Optional[str] = Form(default=None),
    session_id: Optional[str] = Form(default=None),
    mood: Optional[int] = Form(default=None),
    file: Optional[UploadFile] = File(default=None),
    service: JournalService = Depends(get_journal_service),
):
    """Analyze journal entry with optional file upload.
    
    Args:
        text: Journal text
        user_id: User identifier
        session_id: Session identifier
        mood: Mood score (1-5)
        file: Optional file upload
        
    Returns:
        Analysis with emotions, sentiment, insights, recommendations
        
    Raises:
        HTTPException: On validation or processing error
    """
    try:
        # Get text from file if provided, else use text parameter
        entry_text = text.strip() if text else ""
        
        if file:
            try:
                content = await file.read()
                entry_text = content.decode('utf-8').strip()
            except Exception as e:
                _LOG.warning("Could not read file", error=str(e))
                # Fall back to text parameter
        
        if not entry_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Journal text or file is required"
            )
        
        analysis = await service.analyze_journal_entry(
            user_id=user_id or "anonymous",
            text=entry_text,
            mood=mood or 3,
            session_id=session_id,
        )

        _LOG.info("Journal entry uploaded and analyzed", user_id=user_id)
        return analysis

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        _LOG.error("Journal upload analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed"
        )
