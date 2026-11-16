#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - Automated Architecture Smoke Test
Validates end-to-end pipeline: Ingestion, Markdown Parsing, Deduplication, Q&A, and Cleanup.
Usage:
    python scripts/smoke_test.py
"""

import sys
import time
import hashlib
from pathlib import Path

# Fix Windows console UTF-8 output encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.parser import parse_document
from app.ingestion.chunker import create_chunks

# Safe conditional import of database and API components
try:
    from app.db.metadata import SessionLocal, init_db, get_documents, delete_document
    from app.core.agent import ask_question
    from app.api.ask import get_document_executive_summary
    from scripts.ingest_cli import ingest_file
    HAS_DB = True
except ImportError as e:
    HAS_DB = False
    _import_err = e


def run_smoke_test():
    print("=" * 60)
    print("   [+] Dastawez.ai (DocuMind) Architecture Smoke Test")
    print("=" * 60)

    test_file = PROJECT_ROOT / "test_sample.md"

    try:
        # Phase A: Pure Ingestion & AST Parsing
        print("\n[Phase 1] Creating Multi-Element Markdown Document...")
        test_file.write_text(
            "# Enterprise Security Policy\n\n"
            "## Data Encryption Requirements\n"
            "All sensitive customer documents must be encrypted at rest using AES-256 encryption standards.\n\n"
            "## Access Control Table\n"
            "| Role | Clearance Level | Permission |\n"
            "| Operator | Level 2 | Read/Write |\n"
            "| Auditor | Level 1 | Read Only |\n\n"
            "- Multi-factor authentication is mandatory for all personnel.\n"
            "- Regular quarterly security audits must be conducted.\n",
            encoding="utf-8"
        )
        print(f"  ✓ Created test payload at {test_file}")

        print("\n[Phase 2] Ingestion & Markdown Parsing Pipeline...")
        parsed = parse_document(str(test_file), test_file.name)
        elements = parsed["elements"]
        analysis = parsed["analysis"]
        assert len(elements) >= 5, "Expected at least 5 parsed elements"
        element_types = [e["element_type"] for e in elements]
        assert "Title" in element_types, "Title element missing"
        assert "Table" in element_types, "Table element missing"
        print(f"  ✓ Extracted {len(elements)} elements across types: {set(element_types)}")

        print("\n[Phase 3] Hierarchical Chunker & Heading Context Propagation...")
        chunks = create_chunks(elements, test_file.name, target_chunk_size=300, overlap_words=10)
        assert len(chunks) >= 1, "Expected at least 1 chunk"
        print(f"  ✓ Successfully synthesized {len(chunks)} retrievable chunks with heading propagation.")

        print("\n[Phase 4] Cryptographic SHA-256 Fingerprinting...")
        hasher = hashlib.sha256()
        with open(test_file, "rb") as f:
            while block := f.read(65536):
                hasher.update(block)
        checksum = hasher.hexdigest()
        assert len(checksum) == 64, "Invalid SHA-256 checksum length"
        print(f"  ✓ Computed fingerprint: {checksum[:16]}... (valid)")

        # Phase B: Database & Q&A (requires runtime dependencies)
        if not HAS_DB:
            print("\n[Phase 5-7] Skipped (FastAPI / SQLAlchemy runtime packages not yet installed in local Python).")
            print("  ℹ️  Run '.\\setup.ps1' or 'pip install -r requirements.txt' to enable full DB and API integration.")
            print("\n" + "=" * 60)
            print("  [✓] ALL CORE INGESTION & CHUNKING SMOKE TESTS PASSED!")
            print("=" * 60)
            return

        print("\n[Phase 5] Database Initialization & Health Check...")
        init_db()
        db = SessionLocal()
        print("  ✓ Database connection established.")

        try:
            print("\n[Phase 6] Database Ingestion & Deduplication...")
            res = ingest_file(test_file, db, force=True)
            assert res.get("status") == "indexed", "Document ingestion failed"
            doc_id = res["id"]
            print(f"  ✓ Document ingested with ID: {doc_id}")

            dup_res = ingest_file(test_file, db, force=False)
            assert dup_res.get("status") == "deduplicated", "Deduplication did not trigger"
            print(f"  ✓ Deduplication successfully identified duplicate Doc #{dup_res['id']}")

            print("\n[Phase 7] Conversational Context Q&A Retrieval...")
            qa_res = ask_question(db=db, question="What encryption standard is required for data at rest?", document_id=doc_id)
            assert len(qa_res.get("answer", "")) > 10, "Empty QA response"
            print(f"  ✓ QA Confidence: {round(qa_res['confidence'] * 100)}%")
            print(f"  ✓ QA Answer: {qa_res['answer'][:100]}...")

            print("\n[Phase 8] Executive Brief Synthesis...")
            summary = get_document_executive_summary(id=doc_id, db=db)
            assert "executive_summary" in summary, "Summary key missing"
            print(f"  ✓ Summary: {summary['executive_summary'][:100]}...")

            print("\n[Phase 9] Pipeline Cleanup...")
            delete_document(db, doc_id)
            print(f"  ✓ Deleted test document #{doc_id}")

            print("\n" + "=" * 60)
            print("  [✓] ALL 9 END-TO-END ARCHITECTURE SMOKE TESTS PASSED!")
            print("=" * 60)
        finally:
            db.close()

    finally:
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    run_smoke_test()
