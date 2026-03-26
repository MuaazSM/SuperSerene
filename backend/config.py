"""
Centralized configuration management for backend.

Uses environment variables with validation via Pydantic Settings.
Separates configuration from application code.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Application
    APP_NAME: str = "Serene.AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Security & Authentication
    JWT_SECRET: str = ""  # Required - will error if not set
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # OAuth 2.0
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_CALLBACK_URL: str = "http://localhost:8000/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:3000"

    # LLM Providers
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""  # Fallback for Gemini
    GROQ_API_KEY: str = ""

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "serene_ai"

    # Vector Database
    VECTOR_DB_TYPE: str = "faiss"  # "faiss" or "qdrant"
    QDRANT_URL: Optional[str] = None
    RAG_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # External Services
    ASSEMBLYAI_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None

    # Voice Configuration
    VOICE_ENABLED: bool = True
    VOICE_SAMPLE_RATE: int = 16000  # Hz
    VOICE_CHANNELS: int = 1  # Mono
    VOICE_FRAME_SIZE: int = 4096  # Bytes per frame
    VOICE_BUFFER_SIZE: int = 32768  # Max buffer before processing
    VOICE_TIMEOUT_SECONDS: float = 30.0  # Max duration per message
    VOICE_SILENCE_THRESHOLD: float = 0.05  # Amplitude threshold for silence
    VOICE_DEFAULT_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs default (Rachel)
    VOICE_MAX_CHUNK_SIZE: int = 8192  # Max bytes per audio chunk

    # RAG Configuration
    RAG_CHUNK_SIZE: int = 800
    RAG_CHUNK_OVERLAP: int = 200
    RAG_RETRIEVAL_TOP_K: int = 5
    RAG_CONFIDENCE_THRESHOLD: float = 0.6

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_HEAVY_REQUESTS: str = "1/10seconds"  # Safety check, vision analysis
    RATE_LIMIT_MODERATE_REQUESTS: str = "2/10seconds"  # RAG exercise
    RATE_LIMIT_LIGHT_REQUESTS: str = "3/10seconds"  # Chat

    # Cache Configuration
    CACHE_TTL_FAST: int = 60  # Fast-changing data (retrieval cache)
    CACHE_TTL_STABLE: int = 300  # Stable data (exercise cache)

    # Crisis Detection
    CRISIS_RISK_THRESHOLD_HIGH: int = 75
    CRISIS_RISK_THRESHOLD_MEDIUM: int = 60
    CRISIS_RISK_THRESHOLD_LOW: int = 30

    # Memory & Analytics
    EPISODIC_MEMORY_TTL_DAYS: int = 30
    ANALYTICS_AGGREGATION_DAYS: int = 30

    # SMTP (guardian notifications)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_USE_TLS: bool = True

    # Additional Services (legacy support)
    QDRANT_API_KEY: Optional[str] = None
    ASSEMBLY_AI_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None

    # RAG Legacy Configuration
    RAG_TOP_K: Optional[str] = None
    MAX_CHUNK_TOKENS: Optional[str] = None
    ADAPTIVE_DEPTH_MAX: Optional[str] = None

    # Frontend
    NEXT_PUBLIC_API_URL: Optional[str] = None

    # MongoDB Legacy Support
    MONGO_URI: Optional[str] = None
    MONGO_DB: Optional[str] = None

    class Config:
        """Pydantic settings config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables not defined in model

    def validate_required_settings(self) -> None:
        """Validate that all required settings are configured.
        
        Raises:
            ValueError: If required settings are missing.
        """
        if not self.JWT_SECRET:
            raise ValueError("JWT_SECRET environment variable is required")

        if not (self.OPENAI_API_KEY or self.GEMINI_API_KEY or self.GROQ_API_KEY):
            raise ValueError(
                "At least one LLM provider API key is required "
                "(OPENAI_API_KEY, GEMINI_API_KEY, or GROQ_API_KEY)"
            )


# Global settings instance
settings = Settings()
