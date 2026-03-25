"""Collaboration utilities (rewrite) API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.coach import rewrite_message
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)
router = APIRouter(prefix="/api/collab", tags=["collab"])


class RewriteRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to rewrite")
    intent: str = Field(
        default="assertive_kind",
        description="Rewrite intent or tone (e.g., assertive_kind, concise, professional)",
    )
    style: str | None = Field(
        default=None,
        description="Optional style hint; if provided, it overrides intent",
    )


class RewriteResponse(BaseModel):
    rewrittenText: str = Field(..., description="AI rewritten text")
    removed_terms: list[str] = Field(default_factory=list, description="Terms toned down or removed")


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(payload: RewriteRequest) -> RewriteResponse:
    """Rewrite input text with kinder, more assertive framing."""
    intent = payload.style or payload.intent or "assertive_kind"

    try:
        result = rewrite_message(payload.text, intent=intent)
        rewritten = ""
        removed_terms: list[str] = []

        if isinstance(result, dict):
            rewritten = (result.get("rewrite") or "").strip()
            removed_terms = result.get("removed_terms", []) or []

        if not rewritten:
            raise HTTPException(status_code=502, detail="Rewrite failed")

        return RewriteResponse(rewrittenText=rewritten, removed_terms=removed_terms)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive catch
        _LOG.error("rewrite_text failed", error=str(exc))
        raise HTTPException(status_code=500, detail="Internal server error") from exc
