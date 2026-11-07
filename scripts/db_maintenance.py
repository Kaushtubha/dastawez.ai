#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - Database Maintenance and Vacuum Utility
Runs SQLite integrity checks, detects/cleans orphaned chunks, and vacuums fragmented database pages.
Usage:
    python scripts/db_maintenance.py
"""

import os
import sys
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.db.metadata import SessionLocal, Document, Chunk


def run_maintenance():
    db_path = PROJECT_ROOT / "documind.db"
    print(f"[*] Starting Dastawez.ai Database Maintenance on: {db_path}")

    if not db_path.exists():
        print(f"[!] Database file does not exist yet at {db_path}. Run application to initialize.")
        return

    size_before = db_path.stat().st_size
    print(f"[*] Database size before maintenance: {round(size_before / 1024, 2)} KB")

    # 1. SQLite PRAGMA Integrity Check
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA integrity_check;")
        check_result = cursor.fetchall()
        print(f"[+] SQLite PRAGMA integrity_check: {check_result[0][0] if check_result else 'OK'}")

        # 2. Check for Orphaned Chunks
        cursor.execute("""
            SELECT count(*) FROM chunks 
            WHERE document_id NOT IN (SELECT id FROM documents);
        """)
        orphaned_count = cursor.fetchone()[0]

        if orphaned_count > 0:
            print(f"[!] Found {orphaned_count} orphaned chunk(s). Purging...")
            cursor.execute("""
                DELETE FROM chunks 
                WHERE document_id NOT IN (SELECT id FROM documents);
            """)
            conn.commit()
            print(f"[+] Cleaned up {orphaned_count} orphaned chunks.")
        else:
            print("[+] Zero orphaned chunks detected in database catalog.")

        # 3. VACUUM
        print("[*] Executing VACUUM to reclaim free pages and defragment indexes...")
        cursor.execute("VACUUM;")
        conn.commit()
        print("[+] VACUUM completed successfully.")

    finally:
        conn.close()

    size_after = db_path.stat().st_size
    reclaimed = size_before - size_after
    print(f"[*] Database size after maintenance: {round(size_after / 1024, 2)} KB (Reclaimed: {round(reclaimed / 1024, 2)} KB)")

    # 4. Summary counts
    db = SessionLocal()
    try:
        doc_count = db.query(Document).count()
        chunk_count = db.query(Chunk).count()
        print(f"[✓] Maintenance Complete! Total Documents: {doc_count} | Total Chunks: {chunk_count}")
    finally:
        db.close()


if __name__ == "__main__":
    run_maintenance()
