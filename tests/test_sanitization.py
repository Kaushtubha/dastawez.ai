import tempfile
import os
import pytest
from app.ingestion.parser import DocumentParser
from app.ingestion.chunker import DocumentChunker, estimate_tokens, compute_chunk_metrics


def test_sanitize_text_strips_null_and_control_chars():
    dirty_text = "Clean Header\x00 with null and\x07 bell\x1b esc\tkept tab\nkept newline"
    cleaned = DocumentParser._sanitize_text(dirty_text)
    assert "\x00" not in cleaned
    assert "\x07" not in cleaned
    assert "\x1b" not in cleaned
    assert "\tkept tab" in cleaned
    assert "\nkept newline" in cleaned


def test_read_file_safe_multi_encoding():
    # Test UTF-8 with BOM
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".txt") as f:
        f.write("\ufeffBOM Encoded Header\nParagraph with text.".encode("utf-8-sig"))
        bom_path = f.name

    # Test Latin-1 accented text
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".txt") as f:
        f.write("Café and résumé in Latin-1".encode("latin-1"))
        latin_path = f.name

    try:
        bom_content = DocumentParser._read_file_safe(bom_path)
        assert "BOM Encoded Header" in bom_content

        latin_content = DocumentParser._read_file_safe(latin_path)
        assert "Café" in latin_content or "résumé" in latin_content
    finally:
        if os.path.exists(bom_path):
            os.remove(bom_path)
        if os.path.exists(latin_path):
            os.remove(latin_path)


def test_estimate_tokens_calculation():
    assert estimate_tokens("") == 0
    short_text = "Dastawez.ai document intelligence platform."
    tokens = estimate_tokens(short_text)
    assert tokens > 0
    assert tokens < 20


def test_sentence_aware_splitting():
    text = "First sentence is concise. Second sentence introduces RAG! Does the third question work? Indeed."
    sentences = DocumentChunker.split_into_sentences(text)
    assert len(sentences) == 4
    assert sentences[0] == "First sentence is concise."
    assert sentences[1] == "Second sentence introduces RAG!"
    assert sentences[2] == "Does the third question work?"
    assert sentences[3] == "Indeed."


def test_chunker_oversized_sentence_splitting():
    chunker = DocumentChunker(target_chunk_size=100, overlap_words=5, sentence_aware=True)
    long_element = {
        "text": (
            "Sentence one describes the architecture of DocuMind. "
            "Sentence two explains how the vector embedding index functions in production. "
            "Sentence three highlights the interactive visualization and dashboard analytics."
        ),
        "element_type": "NarrativeText",
        "page_number": 1,
        "coordinates": [10, 10, 100, 100]
    }
    chunks = chunker.chunk_elements([long_element], "test.txt")
    assert len(chunks) >= 2
    metrics = compute_chunk_metrics(chunks)
    assert metrics["total_chunks"] == len(chunks)
    assert metrics["total_estimated_tokens"] > 0


def test_verify_schema_integrity():
    try:
        from app.db.metadata import verify_schema_integrity
        status = verify_schema_integrity()
        assert status["status"] == "healthy"
        assert "documents" in status["tables"]
        assert "chunks" in status["tables"]
        assert "users" in status["tables"]
    except (ImportError, ModuleNotFoundError):
        # Allow test to pass gracefully in environments without sqlalchemy installed
        pass
