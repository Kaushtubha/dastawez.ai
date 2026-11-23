import json
import re
from typing import List, Dict, Any, Optional


def estimate_tokens(text: str) -> int:
    """
    Estimates the number of subword tokens for a given text string.
    Uses standard whitespace and character heuristic approximation (1 token ≈ 4 chars or 0.75 words).
    """
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    return max(1, int(round((words / 0.75 + chars / 4.0) / 2)))


class DocumentChunker:
    """
    Chunks structured document elements into retrievable RAG units with sentence-aware
    splitting, word-boundary sliding overlap, hierarchical section heading propagation,
    and structural metadata.
    """

    def __init__(
        self,
        target_chunk_size: int = 800,
        overlap_words: int = 25,
        preserve_heading_context: bool = True,
        sentence_aware: bool = True
    ):
        self.target_chunk_size = target_chunk_size
        self.overlap_words = overlap_words
        self.preserve_heading_context = preserve_heading_context
        self.sentence_aware = sentence_aware

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Splits narrative text on sentence boundaries while preserving semantic continuity."""
        if not text:
            return []
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_elements(
        self,
        elements: List[Dict[str, Any]],
        filename: str
    ) -> List[Dict[str, Any]]:
        if not elements:
            return []

        # Pre-process elements: break oversized narrative elements at sentence boundaries
        processed_elements: List[Dict[str, Any]] = []
        for el in elements:
            text = el.get("text", "").strip()
            if not text:
                continue
            if self.sentence_aware and len(text) > self.target_chunk_size and el.get("element_type") != "Table":
                sentences = self.split_into_sentences(text)
                if len(sentences) > 1:
                    for s in sentences:
                        sub_el = dict(el)
                        sub_el["text"] = s
                        processed_elements.append(sub_el)
                    continue
            processed_elements.append(el)

        if not processed_elements:
            return []

        chunks: List[Dict[str, Any]] = []
        current_text_parts: List[str] = []
        current_size = 0
        current_page = processed_elements[0].get("page_number", 1)
        current_type = processed_elements[0].get("element_type", "NarrativeText")
        current_coords = processed_elements[0].get("coordinates", [100, 100, 500, 150])
        current_heading: Optional[str] = None
        chunk_index = 0

        for el in processed_elements:
            el_text = el.get("text", "").strip()
            if not el_text:
                continue

            el_type = el.get("element_type", "NarrativeText")

            # Track section headers (Title, Header, Subheader)
            if el_type in ("Title", "Header", "Subheader") or el_text.startswith(("# ", "## ", "### ")):
                current_heading = el_text.lstrip("#").strip()

            current_text_parts.append(el_text)
            current_size += len(el_text) + 1

            # When chunk size reaches threshold, flush chunk
            if current_size >= self.target_chunk_size:
                full_chunk_text = " ".join(current_text_parts)
                words = full_chunk_text.split()
                chunk_meta = {
                    "element_type": current_type,
                    "page_number": current_page,
                    "coordinates": current_coords,
                    "filename": filename,
                    "chunk_size": len(full_chunk_text),
                    "word_count": len(words),
                    "estimated_tokens": estimate_tokens(full_chunk_text),
                    "chunk_index": chunk_index,
                    "section_heading": current_heading
                }
                chunks.append({
                    "chunk_text": full_chunk_text,
                    "chunk_metadata_json": json.dumps(chunk_meta)
                })
                chunk_index += 1

                # Extract trailing sliding window overlap words for context continuity
                if self.overlap_words > 0 and len(words) > self.overlap_words:
                    overlap_seed = " ".join(words[-self.overlap_words:])
                    current_text_parts = [overlap_seed]
                    current_size = len(overlap_seed)
                else:
                    current_text_parts = []
                    current_size = 0

                current_page = el.get("page_number", current_page)
                current_type = el.get("element_type", current_type)
                current_coords = el.get("coordinates", current_coords)

        # Flush any remaining text
        if current_text_parts:
            full_chunk_text = " ".join(current_text_parts)
            words = full_chunk_text.split()
            chunk_meta = {
                "element_type": current_type,
                "page_number": current_page,
                "coordinates": current_coords,
                "filename": filename,
                "chunk_size": len(full_chunk_text),
                "word_count": len(words),
                "estimated_tokens": estimate_tokens(full_chunk_text),
                "chunk_index": chunk_index,
                "section_heading": current_heading
            }
            chunks.append({
                "chunk_text": full_chunk_text,
                "chunk_metadata_json": json.dumps(chunk_meta)
            })

        return chunks


def create_chunks(
    elements: List[Dict[str, Any]],
    filename: str,
    target_chunk_size: int = 800,
    overlap_words: int = 25,
    preserve_heading_context: bool = True,
    sentence_aware: bool = True
) -> List[Dict[str, Any]]:
    """Factory helper to partition document elements into chunks."""
    chunker = DocumentChunker(
        target_chunk_size=target_chunk_size,
        overlap_words=overlap_words,
        preserve_heading_context=preserve_heading_context,
        sentence_aware=sentence_aware
    )
    return chunker.chunk_elements(elements, filename)


def compute_chunk_metrics(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes statistical metrics across a generated list of chunks."""
    if not chunks:
        return {
            "total_chunks": 0,
            "avg_word_count": 0,
            "total_characters": 0,
            "total_estimated_tokens": 0
        }

    word_counts = []
    char_counts = []
    token_counts = []
    for c in chunks:
        text = c.get("chunk_text", "")
        char_counts.append(len(text))
        word_counts.append(len(text.split()))
        token_counts.append(estimate_tokens(text))

    return {
        "total_chunks": len(chunks),
        "total_characters": sum(char_counts),
        "total_estimated_tokens": sum(token_counts),
        "avg_characters": round(sum(char_counts) / len(char_counts), 1),
        "avg_word_count": round(sum(word_counts) / len(word_counts), 1),
        "avg_estimated_tokens": round(sum(token_counts) / len(token_counts), 1) if token_counts else 0,
        "min_word_count": min(word_counts),
        "max_word_count": max(word_counts)
    }
