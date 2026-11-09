import json
from typing import List, Dict, Any, Optional

class DocumentChunker:
    """
    Chunks structured document elements into retrievable RAG units with word-boundary
    sliding overlap, hierarchical section heading propagation, and structural metadata.
    """

    def __init__(
        self,
        target_chunk_size: int = 800,
        overlap_words: int = 25,
        preserve_heading_context: bool = True
    ):
        self.target_chunk_size = target_chunk_size
        self.overlap_words = overlap_words
        self.preserve_heading_context = preserve_heading_context

    def chunk_elements(
        self,
        elements: List[Dict[str, Any]],
        filename: str
    ) -> List[Dict[str, Any]]:
        if not elements:
            return []

        chunks: List[Dict[str, Any]] = []
        current_text_parts: List[str] = []
        current_size = 0
        current_page = elements[0].get("page_number", 1)
        current_type = elements[0].get("element_type", "NarrativeText")
        current_coords = elements[0].get("coordinates", [100, 100, 500, 150])
        current_heading: Optional[str] = None
        chunk_index = 0

        for el in elements:
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
    preserve_heading_context: bool = True
) -> List[Dict[str, Any]]:
    """Factory helper to partition document elements into chunks."""
    chunker = DocumentChunker(
        target_chunk_size=target_chunk_size,
        overlap_words=overlap_words,
        preserve_heading_context=preserve_heading_context
    )
    return chunker.chunk_elements(elements, filename)


def compute_chunk_metrics(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes statistical metrics across a generated list of chunks."""
    if not chunks:
        return {"total_chunks": 0, "avg_word_count": 0, "total_characters": 0}

    word_counts = []
    char_counts = []
    for c in chunks:
        text = c.get("chunk_text", "")
        char_counts.append(len(text))
        word_counts.append(len(text.split()))

    return {
        "total_chunks": len(chunks),
        "total_characters": sum(char_counts),
        "avg_characters": round(sum(char_counts) / len(char_counts), 1),
        "avg_word_count": round(sum(word_counts) / len(word_counts), 1),
        "min_word_count": min(word_counts),
        "max_word_count": max(word_counts)
    }
