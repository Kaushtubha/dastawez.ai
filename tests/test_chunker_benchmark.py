import json
import pytest
from app.ingestion.chunker import DocumentChunker, create_chunks, compute_chunk_metrics

def test_document_chunker_heading_propagation():
    """Verify hierarchical section heading is captured and persisted in chunk metadata."""
    elements = [
        {
            "text": "Executive Financial Overview 2026",
            "element_type": "Title",
            "page_number": 1,
            "coordinates": [50, 50, 400, 90]
        },
        {
            "text": "Revenue surged across all cloud document processing tiers by 34% year-over-year.",
            "element_type": "NarrativeText",
            "page_number": 1,
            "coordinates": [50, 100, 400, 150]
        },
        {
            "text": "Operating expenses remained strictly within planned capital constraints.",
            "element_type": "NarrativeText",
            "page_number": 1,
            "coordinates": [50, 160, 400, 210]
        }
    ]

    chunks = create_chunks(elements, "financial_report.pdf", target_chunk_size=300)
    assert len(chunks) >= 1
    chunk = chunks[0]
    meta = json.loads(chunk["chunk_metadata_json"])
    assert "section_heading" in meta
    assert meta["section_heading"] == "Executive Financial Overview 2026"
    assert meta["filename"] == "financial_report.pdf"


def test_compute_chunk_metrics():
    """Verify statistical metric computation across chunks."""
    sample_chunks = [
        {"chunk_text": "One two three four five.", "chunk_metadata_json": "{}"},
        {"chunk_text": "Six seven eight nine ten eleven twelve.", "chunk_metadata_json": "{}"}
    ]
    metrics = compute_chunk_metrics(sample_chunks)
    assert metrics["total_chunks"] == 2
    assert metrics["min_word_count"] == 5
    assert metrics["max_word_count"] == 7
    assert metrics["avg_word_count"] == 6.0
    assert metrics["total_characters"] > 0


def test_chunker_custom_target_and_overlap():
    """Verify chunker respects configurable size and word overlap parameters."""
    chunker = DocumentChunker(target_chunk_size=120, overlap_words=4)
    elements = [
        {"text": "Alpha beta gamma delta epsilon zeta eta theta iota kappa lambda.", "element_type": "NarrativeText"},
        {"text": "Mu nu xi omicron pi rho sigma tau upsilon phi chi psi omega.", "element_type": "NarrativeText"},
        {"text": "The quick brown fox jumps over the lazy sleeping canine dog.", "element_type": "NarrativeText"}
    ]
    chunks = chunker.chunk_elements(elements, "greek.txt")
    assert len(chunks) >= 2
    # Verify metadata fields
    first_meta = json.loads(chunks[0]["chunk_metadata_json"])
    assert first_meta["chunk_index"] == 0
    assert first_meta["word_count"] > 0
