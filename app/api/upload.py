import os
import io
import csv
import json
import shutil
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
    delete_document,
    create_chunk,
    get_chunks_by_document
)
from app.ingestion.parser import parse_document
from app.ingestion.chunker import create_chunks

router = APIRouter()

@router.post("/upload-docs", summary="Upload & Process Document")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Uploads, parses, segments into chunks, and indexes a document."""
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

        db_doc = create_document(
            db=db,
            filename=filename,
            file_path=str(destination_path),
            file_type=f".{ext}",
            file_size=file_size,
            metadata_json=json.dumps(doc_metadata)
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
            "message": "Document uploaded and analyzed successfully",
            "document_id": db_doc.id,
            "filename": filename,
            "file_size": file_size,
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

