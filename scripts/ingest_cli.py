#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - CLI Document Ingestion Utility
Command-line tool for batch or single-file document parsing, chunking, and database indexing.
Usage:
    python scripts/ingest_cli.py --file path/to/document.pdf
    python scripts/ingest_cli.py --dir path/to/documents/
"""

import os
import sys
import time
import json
import hashlib
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.db.metadata import (
    SessionLocal,
    init_db,
    create_document,
    create_chunk,
    get_document_by_hash
)
from app.ingestion.parser import parse_document
from app.ingestion.chunker import create_chunks


def ingest_file(file_path: Path, db, force: bool = False) -> dict:
    if not file_path.exists():
        print(f"[-] File not found: {file_path}")
        return {"error": "File not found"}

    ext = file_path.suffix.lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS:
        print(f"[-] Unsupported extension .{ext} for {file_path.name}")
        return {"error": "Unsupported extension"}

    start_time = time.perf_counter()
    file_size = file_path.stat().st_size

    # Compute SHA-256
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    checksum = hasher.hexdigest()

    existing = get_document_by_hash(db, checksum)
    if existing and not force:
        print(f"[!] Already ingested: {file_path.name} (Doc #{existing.id}). Use --force to re-index.")
        return {"status": "deduplicated", "id": existing.id, "filename": existing.filename}

    print(f"[*] Ingesting: {file_path.name} ({round(file_size / 1024, 1)} KB)...")

    parsed = parse_document(str(file_path), file_path.name)
    elements = parsed.get("elements", [])
    analysis = parsed.get("analysis", {})

    chunks_data = create_chunks(elements, file_path.name)
    duration_ms = int((time.perf_counter() - start_time) * 1000)

    doc_meta = {
        "chunks_added": len(chunks_data),
        "ingested_via": "cli",
        "analysis": analysis
    }

    doc = create_document(
        db=db,
        filename=file_path.name,
        file_path=str(file_path),
        file_type=f".{ext}",
        file_size=file_size,
        metadata_json=json.dumps(doc_meta),
        checksum_sha256=checksum,
        processing_duration_ms=duration_ms,
        status="processed"
    )

    for c in chunks_data:
        create_chunk(
            db=db,
            document_id=doc.id,
            chunk_text=c["chunk_text"],
            chunk_metadata_json=c["chunk_metadata_json"]
        )

    print(f"[+] Successfully indexed Doc #{doc.id}: {len(elements)} elements, {len(chunks_data)} chunks ({duration_ms}ms)")
    return {
        "status": "indexed",
        "id": doc.id,
        "filename": doc.filename,
        "elements": len(elements),
        "chunks": len(chunks_data),
        "duration_ms": duration_ms
    }


def main():
    parser = argparse.ArgumentParser(description="Dastawez.ai Ingestion CLI")
    parser.add_argument("--file", "-f", type=str, help="Single file to ingest")
    parser.add_argument("--dir", "-d", type=str, help="Directory of files to ingest")
    parser.add_argument("--force", action="store_true", help="Force re-indexing even if checksum matches")

    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.print_help()
        sys.exit(1)

    init_db()
    db = SessionLocal()

    try:
        if args.file:
            ingest_file(Path(args.file), db, force=args.force)

        if args.dir:
            dir_path = Path(args.dir)
            if not dir_path.is_dir():
                print(f"[-] Directory not found: {dir_path}")
                sys.exit(1)

            files = [p for p in dir_path.glob("*") if p.is_file() and p.suffix.lower().lstrip(".") in settings.ALLOWED_EXTENSIONS]
            print(f"[*] Found {len(files)} supported document(s) in {dir_path}")
            results = []
            for f in files:
                res = ingest_file(f, db, force=args.force)
                results.append(res)
            print(f"[*] Ingestion batch complete: {len([r for r in results if r.get('status') == 'indexed'])} indexed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
