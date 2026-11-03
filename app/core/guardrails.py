import re
from typing import Dict, Any, List

class Guardrails:
    """Security, input sanitation, and response confidence scoring."""

    @staticmethod
    def sanitize_input(text: str) -> str:
        if not text:
            return ""
        # Remove null bytes and excessive whitespace
        clean = text.replace("\x00", "").strip()
        clean = re.sub(r"\s+", " ", clean)
        return clean[:1000] # Limit query length

    @staticmethod
    def calculate_confidence(
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        generated_answer: str
    ) -> float:
        if not retrieved_chunks:
            return 0.25

        # Top vector score
        best_score = retrieved_chunks[0].get("score", 0.5)

        # Keyword overlap between answer and retrieved text
        retrieved_combined = " ".join(c.get("chunk_text", "") for c in retrieved_chunks).lower()
        query_words = set(re.findall(r"\w{3,}", query.lower()))
        answer_words = set(re.findall(r"\w{3,}", generated_answer.lower()))

        query_in_context = len(query_words.intersection(set(re.findall(r"\w{3,}", retrieved_combined))))
        overlap_ratio = query_in_context / max(1, len(query_words))

        base_conf = 0.5 + (best_score * 0.3) + (overlap_ratio * 0.15)
        # Clamp between 0.35 and 0.98
        return round(min(0.98, max(0.35, base_conf)), 2)

    @staticmethod
    def format_sources(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = []
        seen_refs = set()
        for c in retrieved_chunks:
            meta = c.get("metadata", {})
            filename = meta.get("filename", f"Document #{c.get('document_id', 1)}")
            page = meta.get("page_number", 1)
            el_type = meta.get("element_type", "NarrativeText")
            ref_key = f"{filename}_{page}"
            
            if ref_key not in seen_refs:
                seen_refs.add(ref_key)
                excerpt = c.get("chunk_text", "")[:160] + "..." if len(c.get("chunk_text", "")) > 160 else c.get("chunk_text", "")
                sources.append({
                    "chunk_id": c.get("id"),
                    "filename": filename,
                    "page_number": page,
                    "element_type": el_type,
                    "score": c.get("score", 0.8),
                    "excerpt": excerpt
                })
        return sources

