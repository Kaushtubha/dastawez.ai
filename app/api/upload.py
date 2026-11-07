import os
import io
import csv
import json
import time
import shutil
import hashlib
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.db.metadata import (
    get_db,
    create_document,
    get_documents,
    get_document_by_id,
    get_document_by_hash,
    delete_document,
    create_chunk,
    get_chunks_by_document,
    Chunk
)
from app.ingestion.parser import parse_document
from app.ingestion.chunker import create_chunks

router = APIRouter()

@router.post("/upload-docs", summary="Upload & Process Document")
async def upload_document(
    file: UploadFile = File(...),
    force_reindex: bool = Query(False, description="Force re-indexing even if identical SHA-256 hash exists"),
    db: Session = Depends(get_db)
):
    """Uploads, hashes (SHA-256), parses, segments into chunks, and indexes a document."""
    start_time = time.perf_counter()
    filename = file.filename or "uploaded_document.pdf"
    ext = Path(filename).suffix.lower().lstrip(".")

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Supported formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    settings.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    destination_path = settings.UPLOAD_FOLDER / filename

    try:
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    finally:
        file.file.close()

    file_size = os.path.getsize(destination_path)
    if file_size > settings.MAX_UPLOAD_SIZE:
        if os.path.exists(destination_path):
            os.remove(destination_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size ({settings.MAX_UPLOAD_SIZE // (1024*1024)} MB)"
        )

    # Cryptographic SHA-256 Checksum Calculation
    hasher = hashlib.sha256()
    with open(destination_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    checksum = hasher.hexdigest()

    # Deduplication check
    existing_doc = get_document_by_hash(db, checksum)
    if existing_doc and not force_reindex:
        return {
            "success": True,
            "deduplicated": True,
            "message": "Existing document recognized via SHA-256 fingerprint; returned cached indexing.",
            "document_id": existing_doc.id,
            "filename": existing_doc.filename,
            "file_size": existing_doc.file_size,
            "checksum_sha256": checksum,
            "analysis": existing_doc.to_dict().get("metadata", {}).get("analysis", {})
        }

    try:
        parsed_result = parse_document(str(destination_path), filename)
        elements = parsed_result.get("elements", [])
        analysis = parsed_result.get("analysis", {})

        chunks_data = create_chunks(elements, filename)

        doc_metadata = {
            "chunks_added": len(chunks_data),
            "upload_timestamp": None,
            "analysis": analysis
        }

        processing_duration_ms = int((time.perf_counter() - start_time) * 1000)

        db_doc = create_document(
            db=db,
            filename=filename,
            file_path=str(destination_path),
            file_type=f".{ext}",
            file_size=file_size,
            metadata_json=json.dumps(doc_metadata),
            checksum_sha256=checksum,
            processing_duration_ms=processing_duration_ms,
            status="processed"
        )

        for c in chunks_data:
            create_chunk(
                db=db,
                document_id=db_doc.id,
                chunk_text=c["chunk_text"],
                chunk_metadata_json=c["chunk_metadata_json"]
            )

        return {
            "success": True,
            "deduplicated": False,
            "message": "Document uploaded and analyzed successfully",
            "document_id": db_doc.id,
            "filename": filename,
            "file_size": file_size,
            "checksum_sha256": checksum,
            "processing_duration_ms": processing_duration_ms,
            "total_elements": len(elements),
            "chunks_count": len(chunks_data),
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )


@router.get("/document-history", summary="List All Ingested Documents")
def list_documents(db: Session = Depends(get_db)):
    """Retrieves all uploaded documents with metadata & statistics."""
    docs = get_documents(db)
    return {
        "total": len(docs),
        "documents": [doc.to_dict() for doc in docs]
    }


@router.get("/documents/search", summary="Search Document Catalog and Content")
def search_documents_catalog(
    q: Optional[str] = Query(None, description="Search keyword against filename and extracted text"),
    file_type: Optional[str] = Query(None, description="Optional extension filter (e.g. pdf, docx, txt, md)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Performs server-side filtered search across ingested document catalog and chunk texts.
    """
    from app.db.metadata import Document
    query_builder = db.query(Document)

    if file_type:
        clean_ext = file_type.lower().strip().lstrip(".")
        query_builder = query_builder.filter(Document.file_type.ilike(f"%{clean_ext}%"))

    if q and q.strip():
        term = q.strip()
        # Find document IDs that match filename or have chunks matching term
        matching_chunk_doc_ids = [
            row[0] for row in db.query(Chunk.document_id).filter(Chunk.chunk_text.ilike(f"%{term}%")).distinct().all()
        ]
        query_builder = query_builder.filter(
            (Document.filename.ilike(f"%{term}%")) | (Document.id.in_(matching_chunk_doc_ids))
        )

    total_count = query_builder.count()
    matching_docs = query_builder.order_by(Document.id.desc()).offset(offset).limit(limit).all()

    return {
        "query": q,
        "file_type_filter": file_type,
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "documents": [d.to_dict() for d in matching_docs]
    }



@router.get("/documents/{id}", summary="Get Single Document Details")
def get_document_details(id: int, db: Session = Depends(get_db)):
    """Retrieves specific document details and chunk previews."""
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    chunks = get_chunks_by_document(db, id)
    doc_dict = doc.to_dict()
    doc_dict["chunks"] = [c.to_dict() for c in chunks[:50]]
    doc_dict["chunks_count"] = len(chunks)
    return doc_dict


@router.get("/documents/{id}/export", summary="Export Document Metadata & Chunks")
def export_document_data(
    id: int,
    format: str = Query("json", pattern="^(json|csv)$", description="Export format: json or csv"),
    db: Session = Depends(get_db)
):
    """Exports document structural metrics and text chunks as downloadable JSON or CSV."""
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    chunks = get_chunks_by_document(db, id)
    doc_dict = doc.to_dict()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Chunk_ID", "Document_ID", "Filename", "Page_Number", "Element_Type", "Chunk_Size", "Chunk_Preview"])
        for c in chunks:
            c_dict = c.to_dict()
            meta = c_dict.get("metadata", {})
            clean_text = (c.chunk_text or "").replace("\n", " ").strip()
            writer.writerow([
                c_dict.get("id"),
                doc.id,
                doc.filename,
                meta.get("page_number", 1),
                meta.get("element_type", "NarrativeText"),
                meta.get("chunk_size", len(clean_text)),
                clean_text[:500]
            ])
        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=document_{id}_export.csv"}
        )

    export_payload = {
        "document": doc_dict,
        "total_chunks": len(chunks),
        "chunks": [c.to_dict() for c in chunks]
    }
    return Response(
        content=json.dumps(export_payload, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=document_{id}_export.json"}
    )


@router.delete("/documents/{id}", summary="Delete Document and Chunks")
def remove_document(id: int, db: Session = Depends(get_db)):
    """Deletes a document and its associated chunks and storage file."""
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    success = delete_document(db, id)
    return {"success": success, "message": f"Document {id} deleted successfully"}


class BatchDeleteRequest(BaseModel):
    document_ids: List[int] = Field(
        ...,
        min_length=1,
        description="Array of document IDs to batch remove."
    )


@router.post("/documents/batch-delete", summary="Batch Delete Documents and Chunks")
def batch_remove_documents(req: BatchDeleteRequest, db: Session = Depends(get_db)):
    """
    Deletes multiple documents, their associated vector chunks, and filesystem assets in batch.
    """
    deleted_ids = []
    not_found_ids = []

    for doc_id in req.document_ids:
        doc = get_document_by_id(db, doc_id)
        if not doc:
            not_found_ids.append(doc_id)
            continue
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception:
                pass
        delete_document(db, doc_id)
        deleted_ids.append(doc_id)

    return {
        "success": True,
        "deleted_count": len(deleted_ids),
        "deleted_ids": deleted_ids,
        "not_found_ids": not_found_ids,
        "message": f"Successfully deleted {len(deleted_ids)} documents."
    }


@router.post("/documents/{id}/reindex", summary="Reprocess and Re-index Document")
def reindex_document(id: int, db: Session = Depends(get_db)):
    """
    Purges existing chunks and re-runs layout extraction and chunking pipeline on the stored document file.
    """
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if not doc.file_path or not os.path.exists(doc.file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original document payload not found on disk; cannot re-index."
        )

    start_time = time.perf_counter()
    parsed_result = parse_document(doc.file_path, doc.filename)
    elements = parsed_result.get("elements", [])
    analysis = parsed_result.get("analysis", {})

    chunks_data = create_chunks(elements, doc.filename)

    # Delete previous chunks
    db.query(Chunk).filter(Chunk.document_id == id).delete()

    for c in chunks_data:
        create_chunk(
            db=db,
            document_id=id,
            chunk_text=c["chunk_text"],
            chunk_metadata_json=c["chunk_metadata_json"]
        )

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    meta = doc.to_dict().get("metadata", {})
    meta["analysis"] = analysis
    meta["chunks_added"] = len(chunks_data)
    meta["last_reindexed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    doc.metadata_json = json.dumps(meta)
    doc.processing_duration_ms = duration_ms
    doc.status = "processed"
    db.commit()
    db.refresh(doc)

    return {
        "success": True,
        "message": f"Document {id} re-indexed successfully",
        "document_id": doc.id,
        "total_elements": len(elements),
        "chunks_count": len(chunks_data),
        "processing_duration_ms": duration_ms,
        "analysis": analysis
    }


