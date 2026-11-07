import os
import tempfile
import pytest
from app.ingestion.parser import parse_document
from app.ingestion.chunker import DocumentChunker

def test_markdown_parser_ast_elements():
    """Verify Markdown parser accurately segments titles, tables, lists, and code blocks."""
    md_content = """# Architecture Overview

Here is a system description narrative.

## Component Specifications
| Component | Runtime | Port |
| API Gateway | FastAPI | 8000 |
| Vector Store | Qdrant | 6333 |

Key Architectural Principles:
- Distributed stateless processing
- Grounded contextual attribution
- High-efficiency local vector fallback

```python
def health():
    return {"status": "ok"}
```
"""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(md_content)
        temp_path = f.name

    try:
        parsed = parse_document(temp_path, "test_doc.md")
        elements = parsed["elements"]
        analysis = parsed["analysis"]

        types = [e["element_type"] for e in elements]
        assert "Title" in types
        assert "Table" in types
        assert "ListItem" in types
        assert "CodeBlock" in types
        assert "NarrativeText" in types

        # Check keyword frequency and metrics
        assert analysis["total_elements"] >= 5
        assert "fastapi" in analysis["top_keywords"] or "component" in analysis["top_keywords"]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_chunker_sliding_window_overlap():
    """Verify DocumentChunker preserves word boundary overlap across chunk segments."""
    # Generate long synthetic element text exceeding single chunk target (800 chars)
    long_sentences = [
        f"Paragraph segment index {i} detailing system specifications and verification rules for compliance."
        for i in range(25)
    ]
    elements = [{"text": s, "element_type": "NarrativeText", "page_number": 1} for s in long_sentences]

    chunker = DocumentChunker(target_chunk_size=300, overlap_words=10)
    chunks = chunker.chunk_elements(elements, "compliance_policy.txt")

    assert len(chunks) > 1

    # Verify second chunk includes trailing words from first chunk
    first_words = chunks[0]["chunk_text"].split()
    trailing_overlap = " ".join(first_words[-10:])
    assert trailing_overlap in chunks[1]["chunk_text"]
