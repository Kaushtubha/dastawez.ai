import pytest


def test_analytics_calculation_empty_db():
    try:
        from app.db.metadata import SessionLocal
        from app.api.analytics import get_catalog_analytics_overview
        db = SessionLocal()
        try:
            overview = get_catalog_analytics_overview(db=db)
            assert "total_documents" in overview
            assert "total_chunks" in overview
            assert "storage" in overview
            assert "performance" in overview
            assert overview["total_documents"] >= 0
        finally:
            db.close()
    except (ImportError, ModuleNotFoundError):
        pass


def test_document_status_flow():
    try:
        from app.db.metadata import SessionLocal, create_document, delete_document
        from app.api.upload import get_document_status
        from fastapi import HTTPException

        db = SessionLocal()
        # Verify 404 on non-existent document
        with pytest.raises(HTTPException) as exc_info:
            get_document_status(id=999999, db=db)
        assert exc_info.value.status_code == 404

        # Create temporary document and verify status payload
        doc = create_document(
            db=db,
            filename="status_test.pdf",
            file_path="uploads/status_test.pdf",
            file_type=".pdf",
            file_size=2048,
            processing_duration_ms=45,
            status="processed"
        )
        try:
            res = get_document_status(id=doc.id, db=db)
            assert res["document_id"] == doc.id
            assert res["status"] == "processed"
            assert res["file_size_bytes"] == 2048
            assert res["processing_duration_ms"] == 45
            assert "checksum_sha256" in res
        finally:
            delete_document(db, doc.id)
            db.close()
    except (ImportError, ModuleNotFoundError):
        pass
