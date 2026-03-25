"""Base service class with common patterns for all services."""

from typing import Optional, Dict, Any
from db.mongo import Collections
from core.orchestrator import Orchestrator
from logger.custom_logger import CustomLogger


class BaseService:
    """Base service class providing common functionality.
    
    All services should inherit from this class for consistency:
    - Structured logging
    - Database access
    - Orchestrator access
    """

    def __init__(
        self,
        db: Collections,
        orchestrator: Orchestrator,
    ):
        """Initialize base service.
        
        Args:
            db: MongoDB collections context manager.
            orchestrator: Agent orchestration system.
        """
        self.db = db
        self.orchestrator = orchestrator
        self._logger = CustomLogger().get_logger(self.__class__.__name__)

    @property
    def logger(self):
        """Get logger instance."""
        return self._logger

    def log_info(self, message: str, **kwargs) -> None:
        """Log info level message."""
        self.logger.info(message, **kwargs)

    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning level message."""
        self.logger.warning(message, **kwargs)

    def log_error(self, message: str, **kwargs) -> None:
        """Log error level message."""
        self.logger.error(message, **kwargs)

    def log_debug(self, message: str, **kwargs) -> None:
        """Log debug level message."""
        self.logger.debug(message, **kwargs)
