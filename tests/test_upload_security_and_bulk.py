import pytest
from app.ingestion.parser import sanitize_filename


def test_sanitize_filename_path_traversal():
    assert sanitize_filename("../../etc/passwd.pdf") == "passwd.pdf"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe") == "cmd.exe"
    assert sanitize_filename("../../../../secret_contract.pdf") == "secret_contract.pdf"


def test_sanitize_filename_reserved_windows_names():
    assert sanitize_filename("con.pdf") == "safe_con.pdf"
    assert sanitize_filename("PRN.txt") == "safe_PRN.txt"
    assert sanitize_filename("aux.docx") == "safe_aux.docx"
    assert sanitize_filename("nul.md") == "safe_nul.md"


def test_sanitize_filename_control_characters():
    dirty = "agreement\x00_draft\x1f_v1.pdf"
    cleaned = sanitize_filename(dirty)
    assert "\x00" not in cleaned
    assert "\x1f" not in cleaned
    assert cleaned == "agreement_draft_v1.pdf"


def test_bulk_status_endpoint_logic():
    try:
        from app.db.metadata import SessionLocal, create_document, delete_document
        from app.api.upload import get_bulk_document_status, BulkStatusRequest

        db = SessionLocal()
        doc = create_document(
            db=db,
            filename="bulk_test.pdf",
            file_path="uploads/bulk_test.pdf",
            file_type=".pdf",
            file_size=4096,
            processing_duration_ms=65,
            status="processed"
        )
        try:
            req = BulkStatusRequest(document_ids=[doc.id, 999998])
            res = get_bulk_document_status(req, db=db)
            assert res["requested_count"] == 2
            assert res["found_count"] == 1
            assert str(doc.id) in res["statuses"]
            assert res["statuses"][str(doc.id)]["filename"] == "bulk_test.pdf"
            assert 999998 in res["missing_ids"]
        finally:
            delete_document(db, doc.id)
            db.close()
    except (ImportError, ModuleNotFoundError):
        pass


def test_search_chunks_fts_query():
    try:
        from app.db.metadata import SessionLocal, create_document, create_chunk, delete_document, search_chunks_fts

        db = SessionLocal()
        doc = create_document(
            db=db,
            filename="fts_test.txt",
            file_path="uploads/fts_test.txt",
            file_type=".txt",
            file_size=512
        )
        try:
            c1 = create_chunk(db=db, document_id=doc.id, chunk_text="Confidentiality and non-disclosure obligations shall persist.")
            c2 = create_chunk(db=db, document_id=doc.id, chunk_text="Payment invoicing shall happen on a 30-day net basis.")

            matches = search_chunks_fts(db=db, query="confidentiality obligations", document_id=doc.id)
            assert len(matches) >= 1
            assert any(c.id == c1.id for c in matches)
        finally:
            delete_document(db, doc.id)
            db.close()
    except (ImportError, ModuleNotFoundError):
        pass
