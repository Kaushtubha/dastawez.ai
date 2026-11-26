#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - Directory Auto-Ingestion Watcher Daemon
Monitors an incoming filesystem folder for newly dropped documents (PDF, DOCX, TXT, MD),
verifies magic bytes, performs deduplication, and indexes them into DocuMind automatically.

Usage:
    python scripts/watch_folder.py --once
    python scripts/watch_folder.py --folder incoming/ --interval 5
"""

import sys
import os
import time
import shutil
import hashlib
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows UTF-8 console output support
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def calculate_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def process_file(filepath: Path, db, parser, chunker_fn, move_to: Path = None):
    from app.config import settings
    from app.db.metadata import get_document_by_hash, create_document, create_chunk

    filename = filepath.name
    ext = filepath.suffix.lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS:
        return None

    # Magic byte signature sniffing
    is_valid, reason = parser.validate_magic_bytes(str(filepath), filename)
    if not is_valid:
        print(f"  ❌ Skipping {filename}: Invalid format ({reason})")
        return False

    t0 = time.perf_counter()
    file_size = filepath.stat().st_size
    checksum = calculate_sha256(filepath)

    # Check deduplication
    existing = get_document_by_hash(db, checksum)
    if existing:
        print(f"  ⚡ {filename} already indexed (SHA-256 match #{existing.id})")
        return True

    # Parse and chunk
    try:
        parsed = parser.parse(str(filepath), filename)
        elements = parsed.get("elements", [])
        analysis = parsed.get("analysis", {})
        chunks = chunker_fn(elements, filename)

        duration_ms = int((time.perf_counter() - t0) * 1000)

        # Store in database
        import json
        doc_meta = {"chunks_added": len(chunks), "analysis": analysis}
        doc = create_document(
            db=db,
            filename=filename,
            file_path=str(filepath),
            file_type=f".{ext}",
            file_size=file_size,
            metadata_json=json.dumps(doc_meta),
            checksum_sha256=checksum,
            processing_duration_ms=duration_ms,
            status="processed"
        )
        for c in chunks:
            create_chunk(
                db=db,
                document_id=doc.id,
                chunk_text=c["chunk_text"],
                chunk_metadata_json=c["chunk_metadata_json"]
            )

        print(f"  ✅ Ingested {filename} -> Doc #{doc.id} ({len(chunks)} chunks, {duration_ms}ms)")

        if move_to:
            move_to.mkdir(parents=True, exist_ok=True)
            shutil.move(str(filepath), str(move_to / filename))

        return True
    except Exception as e:
        print(f"  ❌ Failed to process {filename}: {e}")
        return False


def watch_directory(watch_dir: Path, interval: int = 5, run_once: bool = False, move_processed: bool = False):
    from app.db.metadata import SessionLocal
    from app.ingestion.parser import DocumentParser
    from app.ingestion.chunker import create_chunks

    watch_dir.mkdir(parents=True, exist_ok=True)
    processed_dir = (watch_dir / "processed") if move_processed else None

    parser = DocumentParser()
    db = SessionLocal()

    print("=" * 65)
    print("   👁️  DASTAWEZ.AI — INGESTION FOLDER WATCHER DAEMON")
    print(f"[*] Watch Target: {watch_dir.resolve()}")
    print(f"[*] Poll Interval: {interval}s (Single run: {run_once})")
    print("=" * 65)

    try:
        while True:
            files = [
                f for f in watch_dir.iterdir()
                if f.is_file() and not f.name.startswith(".") and f.name != "processed"
            ]

            if files:
                print(f"\n📂 Discovered {len(files)} document(s) in incoming queue...")
                for f in sorted(files):
                    process_file(f, db, parser, create_chunks, processed_dir)

            if run_once:
                print("\n🏁 Single scan pass finished.")
                break

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n👋 Watcher stopped by user.")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Dastawez.ai Ingestion Folder Watcher")
    parser.add_argument("--folder", "-f", type=str, default="incoming", help="Directory path to monitor (default: incoming)")
    parser.add_argument("--interval", "-i", type=int, default=5, help="Poll interval in seconds (default: 5)")
    parser.add_argument("--once", action="store_true", help="Run a single scan pass and exit")
    parser.add_argument("--move-processed", action="store_true", help="Move successfully processed files to processed/ subdir")

    args = parser.parse_args()
    target_path = Path(args.folder)
    if not target_path.is_absolute():
        target_path = PROJECT_ROOT / target_path

    watch_directory(
        watch_dir=target_path,
        interval=args.interval,
        run_once=args.once,
        move_processed=args.move_processed
    )


if __name__ == "__main__":
    main()
