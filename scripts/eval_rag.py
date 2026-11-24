#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - RAG Pipeline & Retrieval Quality Evaluator
Profiles retrieval latency, context keyword overlap, and synthesis confidence
across benchmark questions to evaluate RAG system performance.

Usage:
    python scripts/eval_rag.py
    python scripts/eval_rag.py --top-k 5
    python scripts/eval_rag.py --document-id 1
"""

import sys
import time
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows UTF-8 console output support
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BENCHMARK_QUERIES = [
    "What are the main termination clauses and notice periods?",
    "Summarize the payment terms, invoicing cycle, and late fees.",
    "What are the confidentiality and intellectual property obligations?",
    "Identify all liability caps, exclusions, and indemnification limits.",
    "Who are the designated parties, governing law, and jurisdiction?"
]


def evaluate_rag(top_k: int = 4, doc_id: int = None):
    print("=" * 70)
    print("   📊 DASTAWEZ.AI — RAG RETRIEVAL & SYNTHESIS EVALUATOR")
    print(f"[*] Target Scope: {'Document #' + str(doc_id) if doc_id else 'Global Catalog'}")
    print(f"[*] Top-K Chunks per Query: {top_k}")
    print("=" * 70)

    try:
        from app.db.metadata import SessionLocal, Document
        from app.core.retriever import context_retriever
        from app.core.guardrails import Guardrails
        from app.core.agent import AIAgent
    except ImportError as e:
        print(f"❌ Missing required dependencies: {e}")
        return

    db = SessionLocal()
    agent = AIAgent()

    try:
        doc_count = db.query(Document).count()
        if doc_count == 0:
            print("\n⚠️  No documents found in database. Ingest files using scripts/ingest_cli.py")
            print("   Running synthetic validation instead...\n")

        latencies = []
        confidences = []
        keyword_hits = []

        print(f"\n{'#':<3} {'Query':<40} {'Latency':<10} {'Conf':<8} {'Chunks'}")
        print("-" * 70)

        for idx, query in enumerate(BENCHMARK_QUERIES, 1):
            t0 = time.perf_counter()
            chunks = context_retriever.retrieve(
                db=db,
                query=query,
                document_id=doc_id,
                top_k=top_k
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000
            latencies.append(elapsed_ms)

            # Measure keyword overlap
            query_terms = set(query.lower().split())
            retrieved_text = " ".join(c.get("chunk_text", "") for c in chunks).lower()
            overlap = len([w for w in query_terms if w in retrieved_text])
            keyword_hits.append(overlap)

            # Synthesize answer
            res = agent.ask(db=db, question=query, document_id=doc_id)
            conf = res.get("confidence", 0.0)
            confidences.append(conf)

            q_snippet = (query[:37] + "...") if len(query) > 37 else query
            print(f"{idx:<3} {q_snippet:<40} {elapsed_ms:>6.1f}ms  {int(conf*100):>3}%     {len(chunks)}")

        latencies.sort()
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0

        print("-" * 70)
        print("📈 EVALUATION SUMMARY:")
        print(f"  • Queries Evaluated:    {len(BENCHMARK_QUERIES)}")
        print(f"  • Median Latency (P50): {p50:.2f} ms")
        print(f"  • 95th Percentile (P95): {p95:.2f} ms")
        print(f"  • Average Confidence:   {avg_conf * 100:.1f}%")
        print(f"  • Total Keyword Hits:   {sum(keyword_hits)}")
        print("=" * 70 + "\n")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Dastawez.ai RAG Evaluator")
    parser.add_argument("--top-k", "-k", type=int, default=4, help="Number of chunks to retrieve (default: 4)")
    parser.add_argument("--document-id", "-d", type=int, default=None, help="Target document ID to evaluate")
    args = parser.parse_args()

    evaluate_rag(top_k=args.top_k, doc_id=args.document_id)


if __name__ == "__main__":
    main()
