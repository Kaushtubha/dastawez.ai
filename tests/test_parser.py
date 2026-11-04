import tempfile
import os
from app.ingestion.parser import DocumentParser, parse_document
from app.ingestion.chunker import create_chunks

def test_txt_parsing():
    """Verify text file parsing, element identification, and chunking."""
    sample_text = (
        "TITLE OF LEGAL AGREEMENT\n\n"
        "This is narrative text discussing contract obligations between the parties.\n\n"
        "- Section 1.1 First requirement\n"
        "- Section 1.2 Second requirement\n\n"
        "Table Column 1 | Table Column 2 | Table Column 3\n"
        "Value A | Value B | Value C\n"
    )

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as temp:
        temp.write(sample_text)
        temp_path = temp.name

    try:
        result = parse_document(temp_path, "sample_agreement.txt")
        assert "elements" in result
        assert "analysis" in result
        elements = result["elements"]
        assert len(elements) > 0

        # Check element types detected
        types_detected = {e["element_type"] for e in elements}
        assert "Title" in types_detected or "NarrativeText" in types_detected

        # Check chunking
        chunks = create_chunks(elements, "sample_agreement.txt")
        assert len(chunks) > 0
        assert "chunk_text" in chunks[0]
        assert "chunk_metadata_json" in chunks[0]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
