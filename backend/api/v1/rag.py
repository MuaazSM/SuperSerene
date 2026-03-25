"""RAG (Retrieval-Augmented Generation) API routes using service layer."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from typing import Optional, List
from pydantic import BaseModel

from api.deps import get_current_user, get_db, get_orchestrator
from services.rag_service import RAGService
from services.exercise_service import ExerciseService
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)

router = APIRouter()


def get_rag_service(db=Depends(get_db), orchestrator=Depends(get_orchestrator)) -> RAGService:
    return RAGService(db=db, orchestrator=orchestrator)


def get_exercise_service(db=Depends(get_db), orchestrator=Depends(get_orchestrator)) -> ExerciseService:
    return ExerciseService(db=db, orchestrator=orchestrator)


class RAGQuery(BaseModel):
    query: str
    top_k: int | None = 5


@router.post("/ingest", tags=["rag"])
async def ingest_documents(
    files: Optional[List[UploadFile]] = File(default=None),
    user_id: Optional[str] = Form(default=None),
    tags: Optional[List[str]] = Query(default=None),
    use_local: bool = Query(default=False),
    local_dir: str = Query(default="data/docs"),
    current_user: dict = Depends(get_current_user),
    service: RAGService = Depends(get_rag_service),
):
    try:
        owner_id = user_id or current_user.get("user_id", "system")

        if use_local:
            return await service.ingest_local_dir(directory=local_dir, user_id=owner_id)

        if files:
            content_bytes = [await f.read() for f in files]
            filenames = [f.filename for f in files]
            result = await service.ingest_files(
                files=content_bytes,
                filenames=filenames,
                user_id=owner_id,
                tags=tags or [],
            )
            return {"status": "indexed", **result}

        return {"status": "no_files", "detail": "No files or local directory specified"}
    except Exception as e:
        _LOG.error("Document ingestion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ingestion failed"
        )


@router.get("/status", tags=["rag"])
async def get_ingestion_status(service: RAGService = Depends(get_rag_service)):
    try:
        return await service.status()
    except Exception as e:
        _LOG.error("Failed to get ingestion status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get status"
        )


@router.get("/documents", tags=["rag"])
async def list_documents(
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    service: RAGService = Depends(get_rag_service),
):
    try:
        return await service.list_documents(user_id=user_id, limit=limit, skip=skip)
    except Exception as e:
        _LOG.error("Failed to list documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )


@router.post("/query", tags=["rag"])
async def query_rag(
    payload: RAGQuery,
    service: RAGService = Depends(get_rag_service),
    current_user: dict = Depends(get_current_user),
):
    try:
        top_k = payload.top_k or 5
        result = await service.query(query_text=payload.query, top_k=top_k)
        _LOG.info("RAG query processed", user_id=current_user.get("user_id"))
        return result
    except Exception as e:
        _LOG.error("RAG query failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Query failed"
        )


@router.post("/exercise", tags=["rag"])
async def get_rag_exercise(
    request: dict,
    current_user: dict = Depends(get_current_user),
    service: ExerciseService = Depends(get_exercise_service),
):
    try:
        user_id = current_user.get("user_id")
        context = request.get("context", "")
        mood = request.get("mood", 3)

        recommendations = await service.recommend(
            user_id=user_id,
            mood=mood,
            context=context,
            energy_level=request.get("energy_level", 3),
            count=request.get("count", 3),
        )

        _LOG.info("Exercise recommendation retrieved", user_id=user_id)
        return recommendations
    except Exception as e:
        _LOG.error("Exercise retrieval failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get exercises"
        )
