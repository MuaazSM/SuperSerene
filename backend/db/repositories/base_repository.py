"""Base repository class with common database patterns."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from db.mongo import Collections
from logger.custom_logger import CustomLogger


class BaseRepository:
    """Base repository providing common CRUD patterns.
    
    All repositories should inherit from this class for consistency:
    - Type-safe queries
    - Automatic timestamp management
    - Structured error handling
    """

    # Subclasses should override these
    COLLECTION_NAME: str = None

    def __init__(self, db: Collections):
        """Initialize repository.
        
        Args:
            db: MongoDB collections context manager.
        """
        if self.COLLECTION_NAME is None:
            raise ValueError(f"{self.__class__.__name__} must define COLLECTION_NAME")

        self.db = db
        self._logger = CustomLogger().get_logger(self.__class__.__name__)

    def get_collection(self):
        """Get the MongoDB collection for this repository.
        
        Returns:
            Collection handle.
        """
        return getattr(self.db, self.COLLECTION_NAME)

    async def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID.
        
        Args:
            doc_id: Document ID (string).
            
        Returns:
            Document dict or None if not found.
        """
        try:
            collection = self.get_collection()
            return collection.find_one({"_id": ObjectId(doc_id)})
        except Exception as e:
            self._logger.error(f"Error finding document by ID: {doc_id}", error=str(e))
            return None

    async def find_all(
        self,
        filter_dict: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        """Find documents with optional filtering and pagination.
        
        Args:
            filter_dict: MongoDB filter dict.
            limit: Max documents to return.
            skip: Number of documents to skip.
            
        Returns:
            List of documents.
        """
        try:
            collection = self.get_collection()
            filter_dict = filter_dict or {}
            cursor = collection.find(filter_dict).limit(limit).skip(skip)
            return list(cursor)
        except Exception as e:
            self._logger.error("Error finding documents", error=str(e))
            return []

    async def create(self, data: Dict[str, Any]) -> str:
        """Create new document.
        
        Args:
            data: Document data dict.
            
        Returns:
            Created document ID.
            
        Raises:
            Exception: If insert fails.
        """
        try:
            collection = self.get_collection()
            data["created_at"] = datetime.utcnow()
            data["updated_at"] = datetime.utcnow()
            result = collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            self._logger.error("Error creating document", error=str(e))
            raise

    async def update(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update document by ID.
        
        Args:
            doc_id: Document ID (string).
            updates: Dict of fields to update.
            
        Returns:
            True if document was updated, False otherwise.
        """
        try:
            collection = self.get_collection()
            updates["updated_at"] = datetime.utcnow()
            result = collection.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            self._logger.error(f"Error updating document: {doc_id}", error=str(e))
            return False

    async def delete(self, doc_id: str) -> bool:
        """Delete document by ID.
        
        Args:
            doc_id: Document ID (string).
            
        Returns:
            True if document was deleted, False otherwise.
        """
        try:
            collection = self.get_collection()
            result = collection.delete_one({"_id": ObjectId(doc_id)})
            return result.deleted_count > 0
        except Exception as e:
            self._logger.error(f"Error deleting document: {doc_id}", error=str(e))
            return False

    async def count(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching filter.
        
        Args:
            filter_dict: MongoDB filter dict.
            
        Returns:
            Count of matching documents.
        """
        try:
            collection = self.get_collection()
            filter_dict = filter_dict or {}
            return collection.count_documents(filter_dict)
        except Exception as e:
            self._logger.error("Error counting documents", error=str(e))
            return 0

    async def exists(self, filter_dict: Dict[str, Any]) -> bool:
        """Check if document matching filter exists.
        
        Args:
            filter_dict: MongoDB filter dict.
            
        Returns:
            True if at least one matching document exists.
        """
        try:
            collection = self.get_collection()
            return collection.find_one(filter_dict) is not None
        except Exception as e:
            self._logger.error("Error checking document existence", error=str(e))
            return False
