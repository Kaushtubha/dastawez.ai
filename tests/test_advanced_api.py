import json
import pytest
from fastapi import HTTPException
from app.db.metadata import SessionLocal, create_document, get_document_by_id, delete_document
from app.api.ask import get_document_executive_summary
from app.api.upload import batch_remove_documents, BatchDeleteRequest

def test_document_executive_summary():
    """Verify automated executive summary generation for ingested document."""
    db = SessionLocal()
    try:
        sample_meta = {
            "analysis": {
                "total_pages": 3,
                "total_elements": 18,
                "total_text_length": 2500,
                "element_types": {
                    "Title": 2,
                    "NarrativeText": 12,
                    "ListItem": 4
                },
                "word_frequency": {
                    "agreement": 8,
                    "confidential": 6,
                    "parties": 5
                }
            },
            "chunks": [
                {"text": "Confidential Non-Disclosure Agreement entered into by both parties.", "element_type": "Title"},
                {"text": "The receiving party agrees to safeguard all proprietary information.", "element_type": "NarrativeText"}
            ]
        }

        # Create a sample document with analysis metadata
        test_doc = create_document(
            db=db,
            filename="sample_executive_brief.pdf",
            file_path="/tmp/sample_executive_brief.pdf",
            file_type="application/pdf",
            file_size=10240,
            metadata_json=json.dumps(sample_meta)
        )

        res = get_document_executive_summary(id=test_doc.id, db=db)
        assert res["document_id"] == test_doc.id
        assert "sample_executive_brief.pdf" in res["filename"]
        assert len(res["executive_summary"]) > 20
        assert isinstance(res["key_takeaways"], list)
        assert len(res["key_takeaways"]) > 0
        assert "agreement" in res["key_topics"]
        assert res["metrics"]["total_pages"] == 3
        assert res["metrics"]["total_elements"] == 18

        # Clean up
        delete_document(db, test_doc.id)
    finally:
        db.close()

def test_document_executive_summary_404():
    """Verify 404 response when document ID is nonexistent."""
    db = SessionLocal()
    try:
        with pytest.raises(HTTPException) as exc_info:
            get_document_executive_summary(id=9999999, db=db)
        assert exc_info.value.status_code == 404
    finally:
        db.close()

def test_batch_remove_documents():
    """Verify atomic batch deletion of multiple documents."""
    db = SessionLocal()
    try:
        # Create two test documents
        d1 = create_document(
            db=db,
            filename="batch_test_1.txt",
            file_path="/tmp/batch_test_1.txt",
            file_type="text/plain",
            file_size=512,
            metadata_json=json.dumps({"chunks": []})
        )
        d2 = create_document(
            db=db,
            filename="batch_test_2.txt",
            file_path="/tmp/batch_test_2.txt",
            file_type="text/plain",
            file_size=1024,
            metadata_json=json.dumps({"chunks": []})
        )

        req = BatchDeleteRequest(document_ids=[d1.id, d2.id, 8888888])
        res = batch_remove_documents(req=req, db=db)

        assert res["success"] is True
        assert res["deleted_count"] == 2
        assert d1.id in res["deleted_ids"]
        assert d2.id in res["deleted_ids"]
        assert 8888888 in res["not_found_ids"]

        # Ensure documents no longer exist in DB
        assert get_document_by_id(db, d1.id) is None
        assert get_document_by_id(db, d2.id) is None
    finally:
        db.close()
