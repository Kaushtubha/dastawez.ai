#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - Performance Benchmarking & Pipeline Profiler
Measures throughput and latency across chunking, SHA-256 hashing, SQLite queries, and TF-IDF search.

Usage:
    python scripts/benchmark.py
    python scripts/benchmark.py --iterations 50
"""

import sys
import time
import argparse
import hashlib
from pathlib import Path

# Fix Windows console UTF-8 output encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.chunker import DocumentChunker, create_chunks, compute_chunk_metrics
from app.db.metadata import SessionLocal, init_db, Document
from sqlalchemy import text


def benchmark_chunker(iterations=10):
    print("  [1/4] Profiling Document Chunker & Sliding Window...")
    # Generate synthetic structured elements
    elements = []
    for i in range(200):
        if i % 10 == 0:
            elements.append({
                "text": f"Chapter {i // 10}: Architecture Specifications and Performance Bounds",
                "element_type": "Header",
                "page_number": (i // 20) + 1,
                "coordinates": [50, 50, 500, 80]
            })
        else:
            elements.append({
                "text": f"Element {i}: Enterprise IDP pipelines require predictable latency and high token throughput when handling unstructured legal documents and contracts.",
                "element_type": "NarrativeText",
                "page_number": (i // 20) + 1,
                "coordinates": [50, 100, 500, 200]
            })

    start = time.perf_counter()
    total_chunks = 0
    total_words = 0
    for _ in range(iterations):
        chunks = create_chunks(elements, "bench_sample.pdf", target_chunk_size=600, overlap_words=20)
        total_chunks += len(chunks)
        metrics = compute_chunk_metrics(chunks)
        total_words += metrics["avg_word_count"] * len(chunks)

    duration = time.perf_counter() - start
    ops_per_sec = round(iterations / duration, 1)
    words_per_sec = round(total_words / duration)
    print(f"      ✓ Completed {iterations} chunking runs in {duration:.3f}s")
    print(f"      ✓ Throughput: {ops_per_sec} docs/sec | {words_per_sec:,} words/sec")
    return {"ops_per_sec": ops_per_sec, "words_per_sec": words_per_sec}


def benchmark_hashing(iterations=100):
    print("\n  [2/4] Profiling SHA-256 Checksum Fingerprinting...")
    payload_1mb = b"DocuMind Cryptographic Payload Benchmark String\n" * 20000
    start = time.perf_counter()
    for _ in range(iterations):
        hasher = hashlib.sha256()
        hasher.update(payload_1mb)
        _ = hasher.hexdigest()
    duration = time.perf_counter() - start
    mb_processed = (len(payload_1mb) * iterations) / (1024 * 1024)
    throughput_mb_s = round(mb_processed / duration, 1)
    avg_latency_ms = round((duration / iterations) * 1000, 2)
    print(f"      ✓ Processed {mb_processed:.1f} MB in {duration:.3f}s")
    print(f"      ✓ Speed: {throughput_mb_s} MB/sec | Latency: {avg_latency_ms} ms/MB")
    return {"mb_sec": throughput_mb_s, "latency_ms": avg_latency_ms}


def benchmark_database(iterations=100):
    print("\n  [3/4] Profiling SQLite Query Latency & Connection Pool...")
    init_db()
    db = SessionLocal()
    latencies = []
    try:
        for _ in range(iterations):
            t0 = time.perf_counter()
            db.execute(text("SELECT 1"))
            latencies.append((time.perf_counter() - t0) * 1000)
    finally:
        db.close()

    latencies.sort()
    p50 = round(latencies[len(latencies) // 2], 3)
    p95 = round(latencies[int(len(latencies) * 0.95)], 3)
    p99 = round(latencies[int(len(latencies) * 0.99)], 3)
    avg = round(sum(latencies) / len(latencies), 3)

    print(f"      ✓ Executed {iterations} roundtrip queries")
    print(f"      ✓ Latency: Avg={avg}ms | p50={p50}ms | p95={p95}ms | p99={p99}ms")
    return {"p50_ms": p50, "p95_ms": p95, "avg_ms": avg}


def benchmark_tfidf_search():
    print("\n  [4/4] Profiling TF-IDF Vector Extraction & Query Ranking...")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    corpus = [
        f"Document {i} discusses enterprise security compliance, data residency laws, and encryption at rest with AES-256."
        for i in range(150)
    ]
    query = "encryption at rest and data residency compliance"

    start = time.perf_counter()
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(corpus)
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, matrix).flatten()
    duration = time.perf_counter() - start

    top_idx = scores.argsort()[-3:][::-1]
    latency_ms = round(duration * 1000, 2)
    print(f"      ✓ Indexed 150 documents & executed ranking in {latency_ms}ms")
    print(f"      ✓ Top similarity score: {round(float(scores[top_idx[0]]) * 100, 1)}%")
    return {"latency_ms": latency_ms, "top_score": float(scores[top_idx[0]])}


def main():
    parser = argparse.ArgumentParser(description="Dastawez.ai Pipeline Benchmarking Tool")
    parser.add_argument("--iterations", type=int, default=20, help="Iteration multiplier")
    args = parser.parse_args()

    print("=" * 64)
    print("   [⚡] Dastawez.ai (DocuMind) Architecture Benchmark & Profiler")
    print("=" * 64)

    t_start = time.perf_counter()
    benchmark_chunker(iterations=args.iterations)
    benchmark_hashing(iterations=args.iterations * 3)
    benchmark_database(iterations=args.iterations * 4)
    benchmark_tfidf_search()
    total_time = round(time.perf_counter() - t_start, 2)

    print("\n" + "=" * 64)
    print(f"  [✓] ALL 4 PIPELINE BENCHMARKS COMPLETED IN {total_time}s")
    print("=" * 64)


if __name__ == "__main__":
    main()
