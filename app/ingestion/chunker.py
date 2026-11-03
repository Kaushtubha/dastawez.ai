import json
from typing import List, Dict, Any

class DocumentChunker:
    """Chunks structured document elements into retrievable RAG units."""

    def __init__(self, target_chunk_size: int = 800, overlap: int = 150):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

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
        chunk_index = 0

        for el in elements:
            el_text = el.get("text", "")
            if not el_text:
                continue

            current_text_parts.append(el_text)
            current_size += len(el_text) + 1

            # When chunk size reaches threshold, flush chunk
            if current_size >= self.target_chunk_size:
                full_chunk_text = " ".join(current_text_parts)
                chunk_meta = {
                    "element_type": current_type,
                    "page_number": current_page,
                    "coordinates": current_coords,
                    "filename": filename,
                    "chunk_size": len(full_chunk_text),
                    "chunk_index": chunk_index
                }
                chunks.append({
                    "chunk_text": full_chunk_text,
                    "chunk_metadata_json": json.dumps(chunk_meta)
                })
                chunk_index += 1

                # Retain overlap from the end
                if len(current_text_parts) > 1:
                    current_text_parts = current_text_parts[-1:]
                    current_size = len(current_text_parts[0])
                else:
                    current_text_parts = []
                    current_size = 0

                current_page = el.get("page_number", current_page)
                current_type = el.get("element_type", current_type)
                current_coords = el.get("coordinates", current_coords)

        # Flush any remaining text
        if current_text_parts:
            full_chunk_text = " ".join(current_text_parts)
            chunk_meta = {
                "element_type": current_type,
                "page_number": current_page,
                "coordinates": current_coords,
                "filename": filename,
                "chunk_size": len(full_chunk_text),
                "chunk_index": chunk_index
            }
            chunks.append({
                "chunk_text": full_chunk_text,
                "chunk_metadata_json": json.dumps(chunk_meta)
            })

        return chunks


def create_chunks(elements: List[Dict[str, Any]], filename: str) -> List[Dict[str, Any]]:
    chunker = DocumentChunker()
    return chunker.chunk_elements(elements, filename)

