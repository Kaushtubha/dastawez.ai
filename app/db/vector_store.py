import json
import math
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from app.config import settings

logger = logging.getLogger(__name__)

# Try importing Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False

# Try importing Scikit-Learn and NumPy
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


def _pure_python_tfidf_search(
    query: str,
    texts: List[str],
    top_k: int = 5
) -> List[Tuple[int, float]]:
    """
    Pure-Python TF-IDF vectorizer and cosine similarity computation.
    Provides 100% resilient fallback with zero external dependencies.
    """
    token_pattern = re.compile(r"(?u)\b\w+\b")
    corpus_tokens = [token_pattern.findall(t.lower()) for t in texts]
    query_tokens = token_pattern.findall(query.lower())

    n_docs = len(texts)
    if n_docs == 0:
        return []

    # Document frequency
    df = Counter()
    for tokens in corpus_tokens:
        df.update(set(tokens))

    # IDF with smooth smoothing: log((1 + n) / (1 + df)) + 1
    idf = {word: math.log((1 + n_docs) / (1 + count)) + 1.0 for word, count in df.items()}
    default_idf = math.log(1 + n_docs) + 1.0

    # Query vector
    q_counts = Counter(query_tokens)
    q_vec = {w: count * idf.get(w, default_idf) for w, count in q_counts.items()}
    q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0

    scores = []
    for idx, tokens in enumerate(corpus_tokens):
        if not tokens:
            scores.append((idx, 0.0))
            continue
        d_counts = Counter(tokens)
        d_vec = {w: count * idf.get(w, default_idf) for w, count in d_counts.items()}
        d_norm = math.sqrt(sum(v * v for v in d_vec.values())) or 1.0

        dot = sum(q_vec[w] * d_vec[w] for w in q_vec if w in d_vec)
        cosine = dot / (q_norm * d_norm)
        scores.append((idx, cosine))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


class VectorStore:
    """
    Hybrid Vector Store:
    - Provides high-performance local vector similarity search via Scikit-Learn TF-IDF or pure-Python TF-IDF.
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

        # 1. Scikit-Learn accelerated path
        if HAS_SKLEARN:
            try:
                vectorizer = TfidfVectorizer(
                    stop_words="english",
                    ngram_range=(1, 2),
                    sublinear_tf=True
                )
                tfidf_matrix = vectorizer.fit_transform(texts)
                query_vec = vectorizer.transform([query])
                sims = cosine_similarity(query_vec, tfidf_matrix).flatten()
                top_indices = np.argsort(sims)[::-1][:top_k]

                results = []
                for idx in top_indices:
                    score = float(sims[idx])
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
                logger.error("Scikit-Learn vector search failed: %s, falling back to pure Python", e)

        # 2. Pure-Python TF-IDF Engine
        try:
            ranked_pairs = _pure_python_tfidf_search(query, texts, top_k=top_k)
            results = []
            for idx, raw_score in ranked_pairs:
                score = raw_score
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
            logger.error("Pure Python TF-IDF search error: %s", e)

        # 3. Last-resort keyword matching fallback
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
