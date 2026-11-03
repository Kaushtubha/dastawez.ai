import os
import json
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
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

@router.post("/upload-docs")
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

    # Ensure uploads directory exists
    settings.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    destination_path = settings.UPLOAD_FOLDER / filename

    # Save uploaded file stream
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

    # Parse document elements & metrics
    try:
        parsed_result = parse_document(str(destination_path), filename)
        elements = parsed_result.get("elements", [])
        analysis = parsed_result.get("analysis", {})

        # Generate Chunks
        chunks_data = create_chunks(elements, filename)

        # Update metadata JSON
        doc_metadata = {
            "chunks_added": len(chunks_data),
            "upload_timestamp": None,
            "analysis": analysis
        }

        # Save to database
        db_doc = create_document(
            db=db,
            filename=filename,
            file_path=str(destination_path),
            file_type=f".{ext}",
            file_size=file_size,
            metadata_json=json.dumps(doc_metadata)
        )

        # Save chunks to database
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


@router.get("/document-history")
def list_documents(db: Session = Depends(get_db)):
    """Retrieves all uploaded documents with metadata & statistics."""
    docs = get_documents(db)
    return {
        "total": len(docs),
        "documents": [doc.to_dict() for doc in docs]
    }


@router.get("/documents/{id}")
def get_document_details(id: int, db: Session = Depends(get_db)):
    """Retrieves specific document details and chunk previews."""
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    chunks = get_chunks_by_document(db, id)
    doc_dict = doc.to_dict()
    doc_dict["chunks"] = [c.to_dict() for c in chunks[:50]] # Limit chunk preview
    doc_dict["chunks_count"] = len(chunks)
    return doc_dict


@router.delete("/documents/{id}")
def remove_document(id: int, db: Session = Depends(get_db)):
    """Deletes a document and its associated chunks and storage file."""
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Try deleting file if exists
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    success = delete_document(db, id)
    return {"success": success, "message": f"Document {id} deleted successfully"}

