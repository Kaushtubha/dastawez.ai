#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - Interactive Terminal Document Querying CLI
Allows natural language querying of ingested documents with confidence meters
and cited source excerpts directly from the command line.

Usage:
    python scripts/query_cli.py --list
    python scripts/query_cli.py --query "What is the key terms of the agreement?"
    python scripts/query_cli.py --document-id 1 --query "What is the liability cap?"
    python scripts/query_cli.py (starts interactive REPL)
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows UTF-8 console output support
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def render_confidence_meter(score: float) -> str:
    """Renders a 10-segment ASCII confidence bar."""
    pct = max(0, min(100, int(round(score * 100))))
    filled = int(round(pct / 10))
    bar = "█" * filled + "░" * (10 - filled)
    return f"[{bar}] {pct}%"


def list_documents(db):
    from app.db.metadata import get_documents
    docs = get_documents(db, limit=50)
    print("\n" + "=" * 65)
    print("   📚 INGESTED DOCUMENT CATALOG")
    print("=" * 65)
    if not docs:
        print("  (No documents found in database. Ingest files using scripts/ingest_cli.py)")
        print("=" * 65 + "\n")
        return

    print(f"  {'ID':<5} {'Filename':<35} {'Type':<8} {'Size':<10}")
    print("  " + "-" * 60)
    for d in docs:
        size_str = f"{d.file_size or 0} B"
        if d.file_size and d.file_size > 1024:
            size_str = f"{d.file_size // 1024} KB"
        print(f"  {d.id:<5} {d.filename[:33]:<35} {d.file_type:<8} {size_str:<10}")
    print("=" * 65 + "\n")


def execute_query(agent, db, question: str, doc_id: int = None):
    print(f"\n🔍 Processing query: \"{question}\"")
    if doc_id:
        print(f"🎯 Target Document ID: {doc_id}")

    res = agent.ask(db=db, question=question, document_id=doc_id)
    answer = res.get("answer", "No answer generated.")
    confidence = res.get("confidence", 0.0)
    sources = res.get("sources", [])

    meter = render_confidence_meter(confidence)
    print("\n" + "─" * 65)
    print(f"🤖 Answer: {answer}")
    print(f"📊 Confidence: {meter}")
    print("─" * 65)

    if sources:
        print("\n📖 Cited Sources:")
        for idx, src in enumerate(sources, 1):
            fname = src.get("filename", "unknown")
            page = src.get("page", 1)
            text_snip = src.get("text", "").replace("\n", " ")[:140]
            print(f"  [{idx}] {fname} (Page {page}): \"{text_snip}...\"")
    print()


def interactive_repl(agent, db, initial_doc_id: int = None):
    current_doc_id = initial_doc_id
    print("\n" + "=" * 65)
    print("   💬 DASTAWEZ.AI — INTERACTIVE TERMINAL QUERY REPL")
    print("   Type your question, or ':list', ':doc <id>', ':clear', ':exit'")
    print("=" * 65)

    while True:
        try:
            scope = f"[Doc #{current_doc_id}]" if current_doc_id else "[Global Catalog]"
            prompt_str = f"\nDocuMind {scope}> "
            query = input(prompt_str).strip()

            if not query:
                continue

            if query in (":exit", ":quit", "exit", "quit"):
                print("👋 Exiting query session.")
                break
            elif query in (":list", ":docs"):
                list_documents(db)
            elif query.startswith(":doc"):
                parts = query.split()
                if len(parts) > 1 and parts[1].isdigit():
                    current_doc_id = int(parts[1])
                    print(f"🎯 Focused document set to ID #{current_doc_id}")
                else:
                    current_doc_id = None
                    print("🌐 Reset focus to global document catalog.")
            elif query in (":help", ":h", "help"):
                print("Commands:")
                print("  :list          List all ingested documents")
                print("  :doc <id>      Scope questions to specific document ID (omit ID to reset)")
                print("  :exit / :quit  Exit interactive session")
            else:
                execute_query(agent, db, query, current_doc_id)

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Session ended.")
            break


def main():
    parser = argparse.ArgumentParser(description="Dastawez.ai Interactive Terminal Query CLI")
    parser.add_argument("--query", "-q", type=str, help="Single-shot question string")
    parser.add_argument("--document-id", "-d", type=int, help="Optional document ID to constrain search context")
    parser.add_argument("--list", "-l", action="store_true", help="List all ingested documents and exit")

    args = parser.parse_args()

    try:
        from app.db.metadata import SessionLocal
        from app.core.agent import AIAgent
    except ImportError as e:
        print(f"❌ Missing required dependencies: {e}")
        print("Please ensure your Python environment has dependencies installed: pip install -r requirements.txt")
        sys.exit(1)

    db = SessionLocal()
    agent = AIAgent()

    try:
        if args.list:
            list_documents(db)
            return

        if args.query:
            execute_query(agent, db, args.query, args.document_id)
            return

        interactive_repl(agent, db, args.document_id)
    finally:
        db.close()


if __name__ == "__main__":
    main()
