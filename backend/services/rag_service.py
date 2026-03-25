"""RAG service for ingestion and querying."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path

from services.base_service import BaseService
from rag.rag_pipeline import SingleDocumentIngestor, ConversationalRAG


class RAGService(BaseService):
    """Service for document ingestion and retrieval."""

    def __init__(self, db, orchestrator):
        super().__init__(db, orchestrator)
        self.ingestor = SingleDocumentIngestor()
        self.rag = ConversationalRAG()

    async def ingest_files(
        self,
        files: List[bytes],
        filenames: List[str],
        user_id: str,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        tags = tags or []
        try:
            # Persist metadata placeholders
            for name in filenames:
                self.db.documents.insert_one({
                    "doc_id": f"{user_id}_{name}",
                    "filename": name,
                    "user_id": user_id,
                    "tags": tags,
                    "status": "pending",
                    "created_at": datetime.now(timezone.utc),
                })

            # Delegate to ingestor
            indexed = self.ingestor.ingest_bytes(files, filenames)

            # Mark as indexed
            self.db.documents.update_many(
                {"user_id": user_id, "filename": {"$in": filenames}},
                {"$set": {"status": "indexed", "updated_at": datetime.now(timezone.utc)}}
            )

            return {"indexed": indexed}
        except Exception as e:
            self.log_error("Ingestion failed", error=str(e))
            raise

    async def ingest_local_dir(self, directory: str, user_id: str) -> Dict[str, Any]:
        try:
            paths = [p for p in Path(directory).glob("**/*") if p.is_file()]
            if not paths:
                return {"indexed": 0, "detail": "No files found"}
            indexed = self.ingestor.ingest_files([str(p) for p in paths])
            return {"indexed": indexed, "sources": [str(p) for p in paths]}
        except Exception as e:
            self.log_error("Local ingestion failed", error=str(e))
            raise

    async def status(self) -> Dict[str, Any]:
        total = self.db.documents.count_documents({})
        indexed = self.db.documents.count_documents({"status": "indexed"})
        pending = self.db.documents.count_documents({"status": "pending"})
        return {"total_documents": total, "indexed": indexed, "pending": pending}

    async def list_documents(self, user_id: Optional[str], limit: int, skip: int) -> Dict[str, Any]:
        query = {"user_id": user_id} if user_id else {}
        docs = list(self.db.documents.find(query).skip(skip).limit(limit))
        return {"documents": docs, "total": len(docs)}

    async def query(self, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        try:
            results = self.rag.retrieve(query_text, top_k=top_k)
            return {"results": results, "count": len(results)}
        except Exception as e:
            self.log_warning("RAG query failed", error=str(e))
            return {"results": [], "count": 0, "error": "query_unavailable"}
