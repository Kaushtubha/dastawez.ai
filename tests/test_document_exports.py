import json
import pytest
from app.db.metadata import SessionLocal, init_db, create_document, create_chunk, delete_document
from app.api.upload import export_document_csv, export_document_markdown

def test_export_document_csv():
    """Verify single document chunks export formatted as CSV."""
    init_db()
    db = SessionLocal()
    doc = None
    try:
        doc = create_document(
            db=db,
            filename="export_sample.pdf",
            file_path="/tmp/export_sample.pdf",
            file_type=".pdf",
            file_size=1024,
            metadata_json=json.dumps({"analysis": {"total_elements": 2}})
        )
        chunk_meta = {
            "page_number": 1,
            "element_type": "Title",
            "section_heading": "Confidentiality Terms",
            "word_count": 5
        }
        create_chunk(
            db=db,
            document_id=doc.id,
            chunk_text="All disclosures must remain strictly confidential.",
            chunk_metadata_json=json.dumps(chunk_meta)
        )

        response = export_document_csv(id=doc.id, db=db)
        assert response.status_code == 200
        assert response.media_type == "text/csv"
        assert "export_sample_chunks.csv" in response.headers["Content-Disposition"]

        csv_text = response.body.decode("utf-8")
        assert "chunk_id,document_id,page_number,element_type,section_heading,word_count,chunk_text" in csv_text
        assert "Confidentiality Terms" in csv_text
        assert "All disclosures must remain strictly confidential." in csv_text
    finally:
        if doc:
            delete_document(db, doc.id)
        db.close()


def test_export_document_markdown():
    """Verify single document reconstructed Markdown export with frontmatter."""
    init_db()
    db = SessionLocal()
    doc = None
    try:
        doc = create_document(
            db=db,
            filename="guidelines.md",
            file_path="/tmp/guidelines.md",
            file_type=".md",
            file_size=2048,
            metadata_json=json.dumps({"analysis": {}})
        )
        chunk_meta = {
            "page_number": 1,
            "element_type": "Header",
            "section_heading": "Security Governance",
            "word_count": 8
        }
        create_chunk(
            db=db,
            document_id=doc.id,
            chunk_text="Access control policies must be enforced at all boundaries.",
            chunk_metadata_json=json.dumps(chunk_meta)
        )

        response = export_document_markdown(id=doc.id, db=db)
        assert response.status_code == 200
        assert "text/markdown" in response.media_type
        assert "guidelines_reconstructed.md" in response.headers["Content-Disposition"]

        md_text = response.body.decode("utf-8")
        assert "title: \"guidelines.md\"" in md_text
        assert "## Security Governance" in md_text
        assert "Access control policies must be enforced at all boundaries." in md_text
    finally:
        if doc:
            delete_document(db, doc.id)
        db.close()
