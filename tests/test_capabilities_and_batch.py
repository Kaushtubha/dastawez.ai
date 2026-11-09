import os
import io
import json
import zipfile
import tempfile
import pytest
from app.main import system_capabilities_endpoint
from app.api.upload import reindex_document, export_documents_archive, ExportArchiveRequest
from app.db.metadata import SessionLocal, create_document, create_chunk, delete_document

def test_system_capabilities():
    """Verify system capabilities and feature flags."""
    res = system_capabilities_endpoint()
    assert res["version"] == "1.3.2"
    assert "md" in res["supported_formats"]
    assert "pdf" in res["supported_formats"]
    assert res["features"]["sha256_deduplication"] is True
    assert res["features"]["batch_deletion"] is True
    assert res["features"]["archive_zip_export"] is True
    assert res["features"]["markdown_parser"] is True


def test_document_reindex():
    """Verify document reprocessing and chunk regeneration."""
    db = SessionLocal()
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("Line 1 of reindex test document.\n\nLine 2 containing updated guidelines.\n")
        temp_path = f.name

    try:
        doc = create_document(
            db=db,
            filename="reindex_test.txt",
            file_path=temp_path,
            file_type=".txt",
            file_size=os.path.getsize(temp_path),
            metadata_json=json.dumps({"analysis": {}})
        )

        res = reindex_document(id=doc.id, db=db)
        assert res["success"] is True
        assert res["document_id"] == doc.id
        assert res["total_elements"] >= 2
        assert res["chunks_count"] >= 1

        # Clean up
        delete_document(db, doc.id)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        db.close()


def test_bulk_export_archive_zip():
    """Verify bulk export produces a valid ZIP archive containing manifests and CSV chunks."""
    db = SessionLocal()
    try:
        doc = create_document(
            db=db,
            filename="archive_sample.txt",
            file_path="/tmp/archive_sample.txt",
            file_type=".txt",
            file_size=256,
            metadata_json=json.dumps({"analysis": {}})
        )
        create_chunk(db=db, document_id=doc.id, chunk_text="Sample payload for ZIP export verification.")

        req = ExportArchiveRequest(document_ids=[doc.id], include_raw_files=False)
        response = export_documents_archive(req=req, db=db)

        assert response.status_code == 200
        assert response.media_type == "application/zip"

        # Verify ZIP contents
        with zipfile.ZipFile(io.BytesIO(response.body)) as zf:
            file_list = zf.namelist()
            assert "manifest.json" in file_list
            manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            assert manifest["total_documents"] == 1
            assert manifest["documents"][0]["id"] == doc.id

        delete_document(db, doc.id)
    finally:
        db.close()
