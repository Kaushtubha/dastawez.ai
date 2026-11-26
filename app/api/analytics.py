from typing import Dict, Any
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.metadata import get_db, Document, Chunk

router = APIRouter()


@router.get("/analytics/overview", summary="Get Aggregated Catalog Analytics")
def get_catalog_analytics_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Computes system-wide catalog metrics including format distribution,
    total chunks, storage utilization, and average processing speed.
    """
    total_docs = db.query(Document).count()
    total_chunks = db.query(Chunk).count()

    docs = db.query(Document).all()

    # Format distribution
    format_counts: Dict[str, int] = Counter()
    total_bytes = 0
    processing_durations = []

    for d in docs:
        ext = (d.file_type or "unknown").lower().strip()
        format_counts[ext] += 1
        if d.file_size:
            total_bytes += d.file_size
        if d.processing_duration_ms:
            processing_durations.append(d.processing_duration_ms)

    avg_duration_ms = (
        round(sum(processing_durations) / len(processing_durations), 1)
        if processing_durations else 0.0
    )
    avg_chunks_per_doc = (
        round(total_chunks / max(1, total_docs), 1)
        if total_docs else 0.0
    )

    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "format_distribution": dict(format_counts),
        "storage": {
            "total_bytes": total_bytes,
            "total_kb": round(total_bytes / 1024, 2),
            "total_mb": round(total_bytes / (1024 * 1024), 2)
        },
        "performance": {
            "avg_chunks_per_doc": avg_chunks_per_doc,
            "avg_processing_duration_ms": avg_duration_ms,
            "samples_measured": len(processing_durations)
        }
    }
