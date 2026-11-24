import json
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.metadata import Document, Chunk
from app.db.vector_store import vector_store

class ContextRetriever:
    """
    Hybrid Context Retriever combining vector semantic similarity with
    exact lexical boosting for critical legal/business tokens, numbers, and identifiers.
    """

    @staticmethod
    def _calculate_lexical_boost(query: str, chunk_text: str) -> float:
        """Computes lexical boost based on exact query phrase and identifier overlap."""
        if not query or not chunk_text:
            return 0.0

        query_lower = query.lower()
        chunk_lower = chunk_text.lower()

        # 1. Exact full-query phrase match receives high bonus
        if len(query_lower) > 5 and query_lower in chunk_lower:
            return 0.35

        # 2. Key identifier & alphanumeric terms (e.g. "Section 4.1", "$50,000", "Clause 2")
        alphanumeric_terms = set(re.findall(r"\b[A-Za-z0-9_.-]{3,}\b", query_lower))
        if not alphanumeric_terms:
            return 0.0

        matches = sum(1 for term in alphanumeric_terms if term in chunk_lower)
        ratio = matches / len(alphanumeric_terms)
        return round(ratio * 0.25, 3)

    def retrieve(
        self,
        db: Session,
        query: str,
        document_id: Optional[int] = None,
        top_k: int = 5,
        hybrid_boost: bool = True
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

        # Fetch slightly larger candidate set for hybrid re-ranking
        candidate_k = min(len(chunk_records), max(top_k * 2, 10))
        ranked_chunks = vector_store.search_chunks(query=query, chunks=chunk_records, top_k=candidate_k)

        if not hybrid_boost:
            return ranked_chunks[:top_k]

        # Apply hybrid score fusion: 75% vector score + 25% lexical boost
        for chunk in ranked_chunks:
            raw_vector_score = chunk.get("score", 0.5)
            lex_boost = self._calculate_lexical_boost(query, chunk.get("chunk_text", ""))
            fused_score = min(0.99, round(raw_vector_score * 0.75 + lex_boost, 4))
            chunk["score"] = fused_score
            chunk["lexical_boost"] = lex_boost

        # Sort descending by fused score
        ranked_chunks.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return ranked_chunks[:top_k]


context_retriever = ContextRetriever()

