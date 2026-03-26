"""Main FastAPI application entry point for backend.

This module initializes the FastAPI application with:
- CORS middleware
- Exception handlers
- Rate limiting
- Route registration
- Health check endpoint
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)


# Exception handlers
async def http_exception_handler(request: Request, exc: Exception):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        content={
            "error": getattr(exc, "detail", "Internal Server Error"),
            "status_code": getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown events)."""
    # Startup — validate required config before accepting requests
    try:
        settings.validate_required_settings()
    except ValueError as e:
        _LOG.error("Configuration validation failed", error=str(e))
        raise
    _LOG.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    _LOG.info(f"Environment: debug={settings.DEBUG}")
    
    yield
    
    # Shutdown
    _LOG.info(f"Shutting down {settings.APP_NAME}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Agentic RAG Emotional Wellness System API",
        lifespan=lifespan,
    )

    # Add CORS middleware
    allowed_origins = [settings.FRONTEND_URL]
    if settings.DEBUG:
        allowed_origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add exception handlers
    app.add_exception_handler(Exception, http_exception_handler)

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint for monitoring and load balancers."""
        from db.mongo import get_mongo
        
        db_connected = False
        try:
            db = get_mongo()
            db_connected = db is not None
        except Exception:
            db_connected = False

        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "db_connected": db_connected,
            "ai_enabled": bool(settings.OPENAI_API_KEY or settings.GEMINI_API_KEY),
        }

    # Register routers
    from api import collab
    from api.v1 import auth, journal, chat, analytics, rag, exercises, safety, voice
    from screening.router import router as screening_router
    from routers.guardian import router as guardian_router
    from routers.audit import router as audit_router
    from routers.teletherapy import router as teletherapy_router
    from routers.analytics_dashboard import router as analytics_dashboard_router
    from routers.meditation import router as meditation_router
    from routers.crisis import router as crisis_router

    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(journal.router, prefix="/api/v1/journal", tags=["journal"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(rag.router, prefix="/api/v1/rag", tags=["rag"])
    app.include_router(exercises.router, prefix="/api/v1/exercises", tags=["exercises"])
    app.include_router(safety.router, prefix="/api/v1/safety", tags=["safety"])
    app.include_router(voice.router, prefix="/api/v1", tags=["voice"])
    app.include_router(screening_router, prefix="/api/v1/screening", tags=["screening"])
    app.include_router(guardian_router, prefix="/api/v1/guardian", tags=["guardian"])
    app.include_router(audit_router, prefix="/api/v1/audit", tags=["audit"])
    app.include_router(teletherapy_router, prefix="/api/v1/teletherapy", tags=["teletherapy"])
    app.include_router(analytics_dashboard_router, prefix="/api/v1/analytics/dashboard", tags=["analytics-dashboard"])
    app.include_router(meditation_router, prefix="/api/v1/meditation", tags=["meditation"])
    app.include_router(crisis_router, prefix="/api/v1/crisis", tags=["crisis"])
    app.include_router(collab.router)

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )
