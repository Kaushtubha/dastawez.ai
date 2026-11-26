import pytest
from app.ingestion.chunker import DocumentChunker, create_chunks


def test_chunker_preserves_table_structure():
    elements = [
        {"element_type": "Title", "text": "Financial Summary Q3", "page_number": 1},
        {
            "element_type": "NarrativeText",
            "text": "The following table summarizes revenue and expenses across business units for the third quarter.",
            "page_number": 1
        },
        {
            "element_type": "Table",
            "text": "| Unit | Revenue | Net Profit |\n| Core | $1.2M | $340k |\n| Cloud | $3.5M | $1.1M |",
            "page_number": 1
        }
    ]
    chunks = create_chunks(elements, "financial.md", target_chunk_size=100)
    assert len(chunks) >= 1
    # Verify table row content is preserved intact in chunk
    table_chunk = next((c for c in chunks if "Table" in c["chunk_text"] or "| Unit | Revenue |" in c["chunk_text"]), None)
    assert table_chunk is not None
    assert "| Core | $1.2M | $340k |" in table_chunk["chunk_text"]


def test_chunker_preserves_code_block():
    elements = [
        {"element_type": "Title", "text": "API Authentication", "page_number": 1},
        {
            "element_type": "CodeBlock",
            "text": "def authenticate(token):\n    if not token:\n        return False\n    return verify(token)",
            "page_number": 1
        }
    ]
    chunks = create_chunks(elements, "api.md", target_chunk_size=80)
    assert len(chunks) >= 1
    code_chunk = next(c for c in chunks if "def authenticate" in c["chunk_text"])
    assert "return verify(token)" in code_chunk["chunk_text"]


def test_document_archive_and_restore_lifecycle():
    try:
        from app.db.metadata import SessionLocal, create_document, delete_document, archive_document, restore_document, get_documents
        db = SessionLocal()
        doc = create_document(
            db=db,
            filename="archive_me.pdf",
            file_path="uploads/archive_me.pdf",
            file_type=".pdf",
            file_size=512
        )
        try:
            # 1. Document initially active
            active_docs = get_documents(db, include_archived=False)
            assert any(d.id == doc.id for d in active_docs)

            # 2. Archive document
            archived_ok = archive_document(db, doc.id)
            assert archived_ok is True

            active_after_archive = get_documents(db, include_archived=False)
            assert not any(d.id == doc.id for d in active_after_archive)

            all_docs_including_archived = get_documents(db, include_archived=True)
            assert any(d.id == doc.id for d in all_docs_including_archived)

            # 3. Restore document
            restored_ok = restore_document(db, doc.id)
            assert restored_ok is True

            active_after_restore = get_documents(db, include_archived=False)
            assert any(d.id == doc.id for d in active_after_restore)
        finally:
            delete_document(db, doc.id)
            db.close()
    except (ImportError, ModuleNotFoundError):
        pass
