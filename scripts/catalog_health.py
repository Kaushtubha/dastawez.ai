#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - Catalog Consistency & Storage Health Utility
Audits SQLite database against filesystem uploads, detecting orphaned chunks,
missing payload files, and unindexed storage disk clutter.

Usage:
    python scripts/catalog_health.py
    python scripts/catalog_health.py --fix
"""

import sys
import os
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows UTF-8 console output support
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def inspect_catalog_health(fix_issues: bool = False):
    print("=" * 65)
    print("   🏥 DASTAWEZ.AI — CATALOG HEALTH & INTEGRITY AUDIT")
    print(f"[*] Fix mode enabled: {fix_issues}")
    print("=" * 65)

    from app.config import settings
    from app.db.metadata import SessionLocal, Document, Chunk

    db = SessionLocal()
    try:
        documents = db.query(Document).all()
        chunks = db.query(Chunk).all()
        doc_ids = {d.id for d in documents}

        missing_payloads = []
        for d in documents:
            if not d.file_path or not os.path.exists(d.file_path):
                missing_payloads.append(d)

        orphaned_chunks = [c for c in chunks if c.document_id not in doc_ids]

        # Filesystem audit
        upload_folder = settings.UPLOAD_FOLDER
        unregistered_files = []
        if upload_folder.exists():
            tracked_paths = {Path(d.file_path).resolve() for d in documents if d.file_path}
            for f in upload_folder.iterdir():
                if f.is_file() and not f.name.startswith(".") and f.name != ".gitkeep":
                    if f.resolve() not in tracked_paths:
                        unregistered_files.append(f)

        print("\n📊 AUDIT FINDINGS:")
        print(f"  • Total Registered Documents: {len(documents)}")
        print(f"  • Total Extracted Chunks:     {len(chunks)}")
        print(f"  • Missing Storage Payloads:   {len(missing_payloads)}")
        print(f"  • Orphaned Vector Chunks:     {len(orphaned_chunks)}")
        print(f"  • Untracked Files in Storage: {len(unregistered_files)}")

        if orphaned_chunks:
            print(f"\n⚠️  Found {len(orphaned_chunks)} orphaned chunks!")
            if fix_issues:
                orphan_ids = [c.id for c in orphaned_chunks]
                db.query(Chunk).filter(Chunk.id.in_(orphan_ids)).delete(synchronize_session=False)
                db.commit()
                print(f"  ✅ Purged {len(orphan_ids)} orphaned chunks from database.")

        if missing_payloads:
            print(f"\n⚠️  {len(missing_payloads)} documents reference missing files on disk:")
            for d in missing_payloads[:5]:
                print(f"    - Doc #{d.id}: {d.filename} ({d.file_path})")

        if unregistered_files:
            print(f"\nℹ️  {len(unregistered_files)} files in storage are not tracked in catalog:")
            for f in unregistered_files[:5]:
                print(f"    - {f.name} ({f.stat().st_size} bytes)")

        if not missing_payloads and not orphaned_chunks and not unregistered_files:
            print("\n✨ Catalog and storage are 100% consistent and healthy!")

        print("\n" + "=" * 65)

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Dastawez.ai Catalog Consistency Audit")
    parser.add_argument("--fix", action="store_true", help="Automatically purge orphaned chunks")
    args = parser.parse_args()

    inspect_catalog_health(fix_issues=args.fix)


if __name__ == "__main__":
    main()
