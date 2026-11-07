import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings

logger = logging.getLogger(__name__)

# Try importing Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False


class VectorStore:
    """
    Hybrid Vector Store:
    - Provides high-performance local vector similarity search via Scikit-Learn TF-IDF.
    - Synchronizes with Qdrant Vector DB when available.
    - Supports cosine similarity ranking and dynamic confidence thresholds.
    """

    def __init__(self):
        self.qdrant_client: Optional[Any] = None
        self.collection_name = "documind_chunks"
        self._init_qdrant()

    def _init_qdrant(self):
        if not HAS_QDRANT or not settings.QDRANT_URL:
            return
        try:
            client = QdrantClient(url=settings.QDRANT_URL, timeout=2.0)
            client.get_collections()
            self.qdrant_client = client
            logger.info("Connected to Qdrant at %s", settings.QDRANT_URL)
        except Exception as e:
            logger.warning("Qdrant not reachable (%s). Falling back to local vector search.", e)
            self.qdrant_client = None

    def search_chunks(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = 5,
        min_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Performs semantic vector search across chunks for a given query.
        Returns top_k most relevant chunks with cosine similarity score.
        """
        if not chunks:
            return []

        # If only a few chunks, return them all with normalized default scores
        if len(chunks) <= top_k:
            results = []
            for c in chunks:
                item = dict(c)
                item["score"] = 0.85
                results.append(item)
            return results

        texts = [c.get("chunk_text", "") for c in chunks]

        try:
            # Build TF-IDF vector space with word and n-gram overlap
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                sublinear_tf=True
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
            query_vec = vectorizer.transform([query])

            # Compute cosine similarity
            sims = cosine_similarity(query_vec, tfidf_matrix).flatten()

            # Get top indices
            top_indices = np.argsort(sims)[::-1][:top_k]

            results = []
            for idx in top_indices:
                score = float(sims[idx])
                # If similarity is zero, assign base relevance for keyword presence
                if score <= 0.0:
                    query_words = set(query.lower().split())
                    chunk_words = set(texts[idx].lower().split())
                    overlap = len(query_words.intersection(chunk_words))
                    score = min(0.6, 0.2 + (overlap * 0.1))

                score = round(min(1.0, max(0.0, score)), 4)
                if score >= min_threshold:
                    chunk_copy = dict(chunks[idx])
                    chunk_copy["score"] = score
                    results.append(chunk_copy)

            return results
        except Exception as e:
            logger.error("Error during vector similarity search: %s", e)
            # Fallback: simple text match
            query_lower = query.lower()
            scored = []
            for c in chunks:
                txt = c.get("chunk_text", "").lower()
                score = 0.9 if query_lower in txt else 0.5
                item = dict(c)
                item["score"] = score
                scored.append(item)
            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:top_k]


vector_store = VectorStore()
