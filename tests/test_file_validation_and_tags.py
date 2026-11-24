import os
import tempfile
import pytest
from app.ingestion.parser import DocumentParser
from app.core.retriever import ContextRetriever


def test_magic_bytes_valid_pdf():
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".pdf") as f:
        f.write(b"%PDF-1.5\n%trailer\n%%EOF")
        path = f.name
    try:
        is_valid, reason = DocumentParser.validate_magic_bytes(path, "contract.pdf")
        assert is_valid is True
        assert reason == "valid_pdf"
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_magic_bytes_reject_executable_disguised_as_pdf():
    # DOS / Windows executable header MZ
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".pdf") as f:
        f.write(b"MZ\x90\x00\x03\x00\x00\x00This is malicious binary code")
        path = f.name
    try:
        is_valid, reason = DocumentParser.validate_magic_bytes(path, "exploit.pdf")
        assert is_valid is False
        assert "executable" in reason.lower()
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_magic_bytes_valid_docx():
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".docx") as f:
        f.write(b"PK\x03\x04\x14\x00\x06\x00[Content_Types].xml")
        path = f.name
    try:
        is_valid, reason = DocumentParser.validate_magic_bytes(path, "report.docx")
        assert is_valid is True
        assert reason == "valid_docx"
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_magic_bytes_reject_binary_text():
    # Text file containing forbidden binary null bytes
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".txt") as f:
        f.write(b"Text content with \x00 binary injection bytes")
        path = f.name
    try:
        is_valid, reason = DocumentParser.validate_magic_bytes(path, "notes.txt")
        assert is_valid is False
        assert "binary" in reason.lower()
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_lexical_boost_calculation():
    query = "What is the liability cap under Section 12.4?"
    matching_chunk = "As stated in Section 12.4, the total aggregate liability cap shall not exceed $100,000."
    unrelated_chunk = "The cafeteria will be open from 9 AM to 5 PM on weekdays."

    boost_match = ContextRetriever._calculate_lexical_boost(query, matching_chunk)
    boost_unrelated = ContextRetriever._calculate_lexical_boost(query, unrelated_chunk)

    assert boost_match > 0.1
    assert boost_unrelated == 0.0


def test_update_document_tags_logic():
    try:
        from app.db.metadata import SessionLocal, create_document, delete_document, update_document_tags
        db = SessionLocal()
        doc = create_document(
            db=db,
            filename="tagged_doc.pdf",
            file_path="uploads/tagged_doc.pdf",
            file_type=".pdf",
            file_size=1024
        )
        try:
            updated = update_document_tags(db, doc.id, ["Legal", "Contract", "  Legal  ", "Q4"])
            assert updated is not None
            tags = updated.to_dict()["metadata"]["tags"]
            assert sorted(tags) == ["Contract", "Legal", "Q4"]
        finally:
            delete_document(db, doc.id)
            db.close()
    except (ImportError, ModuleNotFoundError):
        pass
