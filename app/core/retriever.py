import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.metadata import Document, Chunk
from app.db.vector_store import vector_store

class ContextRetriever:
    """Retrieves document chunks matching query intent."""

    def retrieve(
        self,
        db: Session,
        query: str,
        document_id: Optional[int] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        # Query chunks from database
        chunk_query = db.query(Chunk)
        if document_id:
            chunk_query = chunk_query.filter(Chunk.document_id == document_id)

        db_chunks = chunk_query.all()
        if not db_chunks:
            return []

        # Prepare formatted chunk dicts for vector ranking
        chunk_records = []
        for c in db_chunks:
            meta = {}
            if c.chunk_metadata_json:
                try:
                    meta = json.loads(c.chunk_metadata_json)
                except Exception:
                    meta = {}
            chunk_records.append({
                "id": c.id,
                "document_id": c.document_id,
                "chunk_text": c.chunk_text or "",
                "metadata": meta
            })

        # Run vector similarity search
        ranked_chunks = vector_store.search_chunks(query=query, chunks=chunk_records, top_k=top_k)
        return ranked_chunks


context_retriever = ContextRetriever()

