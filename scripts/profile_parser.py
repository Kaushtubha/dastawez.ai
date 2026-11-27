#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - Document Parser Memory & Latency Profiler
Profiles parsing throughput, peak RAM allocation (tracemalloc),
and element classification across document formats.

Usage:
    python scripts/profile_parser.py
    python scripts/profile_parser.py --file path/to/document.pdf
"""

import sys
import time
import tempfile
import tracemalloc
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows UTF-8 console output support
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def generate_sample_files():
    samples = {}

    # TXT
    f_txt = tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt")
    f_txt.write("TERMS OF SERVICE\n\n" + "This agreement governs the use of DocuMind software.\n\n" * 20)
    f_txt.close()
    samples["Plain Text (.txt)"] = f_txt.name

    # Markdown
    f_md = tempfile.NamedTemporaryFile("w", delete=False, suffix=".md")
    f_md.write("# Project Overview\n\n## Section 1\nDetailed content paragraph.\n\n| Col A | Col B |\n| --- | --- |\n| Val 1 | Val 2 |\n")
    f_md.close()
    samples["Markdown (.md)"] = f_md.name

    # RTF
    f_rtf = tempfile.NamedTemporaryFile("w", delete=False, suffix=".rtf")
    f_rtf.write("{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Arial;}} \\fs24 \\b Legal Notice \\b0 \\par All rights reserved.\\par}")
    f_rtf.close()
    samples["Rich Text (.rtf)"] = f_rtf.name

    return samples


def profile_file(parser, file_path: str, label: str):
    tracemalloc.start()
    t0 = time.perf_counter()

    res = parser.parse(file_path, Path(file_path).name)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elements_count = len(res.get("elements", []))
    keywords_count = len(res.get("analysis", {}).get("top_keywords", []))

    print(f"  {label:<22} | {elapsed_ms:>8.2f} ms | {peak_mem / 1024:>8.1f} KB | {elements_count:>8} | {keywords_count:>8}")


def run_profiler(target_file: str = None):
    from app.ingestion.parser import DocumentParser
    parser = DocumentParser()

    print("=" * 70)
    print("   ⏱️  DASTAWEZ.AI — PARSER MEMORY & LATENCY PROFILER")
    print("=" * 70)
    print(f"  {'Format':<22} | {'Latency':<11} | {'Peak RAM':<11} | {'Elements':<8} | {'Keywords'}")
    print("-" * 70)

    if target_file:
        p = Path(target_file)
        if not p.exists():
            print(f"❌ Target file does not exist: {target_file}")
            return
        profile_file(parser, str(p), p.suffix.upper())
    else:
        samples = generate_sample_files()
        try:
            for label, path in samples.items():
                profile_file(parser, path, label)
        finally:
            for path in samples.values():
                Path(path).unlink(missing_ok=True)

    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Dastawez.ai Parser Memory & Latency Profiler")
    parser.add_argument("--file", "-f", type=str, help="Specific file path to profile")
    args = parser.parse_args()

    run_profiler(target_file=args.file)


if __name__ == "__main__":
    main()
