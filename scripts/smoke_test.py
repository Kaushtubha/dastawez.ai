#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - Automated Architecture Smoke Test
Validates end-to-end pipeline: Ingestion, Markdown Parsing, Deduplication, Q&A, and Cleanup.
Usage:
    python scripts/smoke_test.py
"""

import sys
from pathlib import Path

# Fix Windows console UTF-8 output encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.db.metadata import SessionLocal, init_db, get_documents, delete_document
from app.ingestion.parser import parse_document
from app.ingestion.chunker import create_chunks
from app.core.agent import ask_question
from app.api.ask import get_document_executive_summary
from scripts.ingest_cli import ingest_file


def run_smoke_test():
    print("=" * 60)
    print("   [+] Dastawez.ai (DocuMind) Architecture Smoke Test")
    print("=" * 60)

    # Phase 1: Initialize Database
    print("\n[Phase 1] Database Initialization & Health Check...")
    init_db()
    db = SessionLocal()
    print("  ✓ Database connection established.")

    test_file = PROJECT_ROOT / "test_sample.md"
    try:
        # Phase 2: Create Test Markdown File
        print("\n[Phase 2] Creating Multi-Element Markdown Document...")
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

        # Phase 3: Ingestion & Parsing
        print("\n[Phase 3] Ingestion & Markdown Parsing Pipeline...")
        res = ingest_file(test_file, db, force=True)
        assert res.get("status") == "indexed", "Document ingestion failed"
        doc_id = res["id"]
        print(f"  ✓ Document ingested with ID: {doc_id}")
        print(f"  ✓ Elements: {res['elements']} | Chunks: {res['chunks']}")

        # Phase 4: SHA-256 Deduplication Verification
        print("\n[Phase 4] Cryptographic SHA-256 Deduplication Test...")
        dup_res = ingest_file(test_file, db, force=False)
        assert dup_res.get("status") == "deduplicated", "Deduplication did not trigger"
        print(f"  ✓ Deduplication successfully identified duplicate Doc #{dup_res['id']}")

        # Phase 5: Conversational Q&A Retrieval Agent
        print("\n[Phase 5] Conversational Context Q&A Retrieval...")
        qa_res = ask_question(db=db, question="What encryption standard is required for data at rest?", document_id=doc_id)
        assert len(qa_res.get("answer", "")) > 10, "Empty QA response"
        print(f"  ✓ QA Confidence: {round(qa_res['confidence'] * 100)}%")
        print(f"  ✓ QA Answer: {qa_res['answer'][:120]}...")

        # Phase 6: Executive Summary Synthesis
        print("\n[Phase 6] Executive Brief Synthesis...")
        summary = get_document_executive_summary(id=doc_id, db=db)
        assert "executive_summary" in summary, "Summary key missing"
        print(f"  ✓ Summary: {summary['executive_summary'][:120]}...")

        # Phase 7: Cleanup
        print("\n[Phase 7] Pipeline Cleanup...")
        delete_document(db, doc_id)
        print(f"  ✓ Deleted test document #{doc_id}")

        print("\n" + "=" * 60)
        print("  [✓] ALL 7 ARCHITECTURE SMOKE TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)

    finally:
        if test_file.exists():
            test_file.unlink()
        db.close()


if __name__ == "__main__":
    run_smoke_test()
