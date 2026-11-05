import pytest
import json
import csv
import io
import sys
from app.api.upload import export_document_data
from app.db.metadata import SessionLocal, get_documents
from fastapi import HTTPException

# Increase field size limit for CSV reader testing
csv.field_size_limit(min(sys.maxsize, 2147483647))

def test_export_document_json():
    """Verify document export in JSON format."""
    db = SessionLocal()
    try:
        docs = get_documents(db)
        if not docs:
            pytest.skip("No documents in database to export")

        doc_id = docs[0].id
        response = export_document_data(id=doc_id, format="json", db=db)
        assert response.status_code == 200
        assert response.media_type == "application/json"
        
        payload = json.loads(response.body.decode("utf-8"))
        assert "document" in payload
        assert "total_chunks" in payload
        assert "chunks" in payload
        assert payload["document"]["id"] == doc_id
    finally:
        db.close()

def test_export_document_csv():
    """Verify document export in CSV format."""
    db = SessionLocal()
    try:
        docs = get_documents(db)
        if not docs:
            pytest.skip("No documents in database to export")

        doc_id = docs[0].id
        response = export_document_data(id=doc_id, format="csv", db=db)
        assert response.status_code == 200
        assert response.media_type == "text/csv"

        csv_reader = csv.reader(io.StringIO(response.body.decode("utf-8")))
        rows = list(csv_reader)
        assert len(rows) > 0
        header = rows[0]
        assert "Chunk_ID" in header
        assert "Document_ID" in header
        assert "Page_Number" in header
        assert "Element_Type" in header
    finally:
        db.close()

def test_export_nonexistent_document():
    """Verify 404 is raised for non-existent document export."""
    db = SessionLocal()
    try:
        with pytest.raises(HTTPException) as exc:
            export_document_data(id=999999, format="json", db=db)
        assert exc.value.status_code == 404
    finally:
        db.close()
