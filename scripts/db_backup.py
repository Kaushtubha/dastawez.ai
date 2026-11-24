#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - Database Backup & Restoration Utility
Performs consistent SQLite database snapshots, gzip compression,
and integrity-verified restoration.

Usage:
    python scripts/db_backup.py --backup
    python scripts/db_backup.py --list
    python scripts/db_backup.py --restore backups/documind_backup_xxx.db.gz
"""

import sys
import os
import gzip
import shutil
import sqlite3
import argparse
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows UTF-8 console output support
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def get_db_path() -> Path:
    from app.config import settings
    db_url = settings.DATABASE_URL
    if "sqlite:///" in db_url:
        raw_path = db_url.split("sqlite:///", 1)[1]
        return Path(raw_path).resolve()
    return (PROJECT_ROOT / "documind.db").resolve()


def perform_backup(output_dir: Path = None) -> Path:
    db_path = get_db_path()
    if not db_path.exists():
        print(f"❌ Database file not found at: {db_path}")
        sys.exit(1)

    if not output_dir:
        output_dir = PROJECT_ROOT / "backups"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    temp_snapshot = output_dir / f"temp_{timestamp}.db"
    compressed_file = output_dir / f"documind_backup_{timestamp}.db.gz"

    print("=" * 65)
    print("   💾 DASTAWEZ.AI — DATABASE BACKUP GENERATOR")
    print(f"[*] Source Database: {db_path}")
    print(f"[*] Target Archive:  {compressed_file}")
    print("-" * 65)

    try:
        # Create consistent atomic snapshot using SQLite online backup API
        source_conn = sqlite3.connect(db_path)
        dest_conn = sqlite3.connect(temp_snapshot)
        with dest_conn:
            source_conn.backup(dest_conn, pages=100)
        dest_conn.close()
        source_conn.close()

        # Compress snapshot with gzip
        with open(temp_snapshot, "rb") as f_in, gzip.open(compressed_file, "wb", compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)

        orig_size = temp_snapshot.stat().st_size
        comp_size = compressed_file.stat().st_size
        compression_ratio = ((orig_size - comp_size) / max(1, orig_size)) * 100

        print("✅ Snapshot created successfully.")
        print(f"  • Uncompressed Size: {orig_size / 1024:.1f} KB")
        print(f"  • Compressed Size:   {comp_size / 1024:.1f} KB ({compression_ratio:.1f}% space saved)")
        print("=" * 65)
        return compressed_file

    finally:
        if temp_snapshot.exists():
            temp_snapshot.unlink()


def list_backups(output_dir: Path = None):
    if not output_dir:
        output_dir = PROJECT_ROOT / "backups"
    print("=" * 65)
    print("   📂 STORED DATABASE BACKUPS")
    print(f"[*] Location: {output_dir}")
    print("-" * 65)

    if not output_dir.exists():
        print("  (No backups directory found)")
        print("=" * 65)
        return

    backups = sorted(output_dir.glob("documind_backup_*.db.gz"), reverse=True)
    if not backups:
        print("  (No backup archives found)")
        print("=" * 65)
        return

    print(f"  {'Filename':<42} {'Size':<10} {'Created'}")
    print("  " + "-" * 60)
    for b in backups:
        size_kb = f"{b.stat().st_size / 1024:.1f} KB"
        mtime = datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {b.name:<42} {size_kb:<10} {mtime}")
    print("=" * 65)


def restore_backup(archive_path: Path):
    if not archive_path.exists():
        print(f"❌ Backup archive not found: {archive_path}")
        sys.exit(1)

    db_path = get_db_path()
    temp_restored = db_path.parent / f"restore_temp_{int(datetime.now().timestamp())}.db"

    print("=" * 65)
    print("   ♻️ DASTAWEZ.AI — DATABASE RESTORATION")
    print(f"[*] Archive: {archive_path}")
    print(f"[*] Destination: {db_path}")
    print("-" * 65)

    try:
        # Decompress archive to temporary database file
        with gzip.open(archive_path, "rb") as f_in, open(temp_restored, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        # Verify integrity of decompressed database
        conn = sqlite3.connect(temp_restored)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        check_res = cursor.fetchall()
        conn.close()

        if check_res != [("ok",)]:
            print(f"❌ Integrity check failed for restored database: {check_res}")
            sys.exit(1)

        # Replace target database file
        if db_path.exists():
            safety_copy = db_path.parent / f"{db_path.name}.safety_bak"
            shutil.copy2(db_path, safety_copy)
            print(f"[*] Created safety copy at: {safety_copy}")

        shutil.move(temp_restored, db_path)
        print("✅ Database successfully restored and integrity verified.")
        print("=" * 65)

    finally:
        if temp_restored.exists():
            temp_restored.unlink()


def main():
    parser = argparse.ArgumentParser(description="Dastawez.ai Database Backup & Restoration Utility")
    parser.add_argument("--backup", action="store_true", help="Generate compressed backup snapshot")
    parser.add_argument("--list", action="store_true", help="List all available backup archives")
    parser.add_argument("--restore", type=str, help="Path to .db.gz archive to restore")

    args = parser.parse_args()

    if args.list:
        list_backups()
    elif args.restore:
        restore_backup(Path(args.restore))
    elif args.backup:
        perform_backup()
    else:
        perform_backup()


if __name__ == "__main__":
    main()
