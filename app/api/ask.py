from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.metadata import get_db, get_document_by_id, get_documents
from app.core.agent import ask_question

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    document_id: Optional[int] = None

class AskResponse(BaseModel):
    question: str
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]

@router.post("/ask", response_model=AskResponse)
def ask_document_endpoint(
    req: AskRequest,
    db: Session = Depends(get_db)
):
    """Ask natural language questions about one or all processed documents."""
    result = ask_question(db=db, question=req.question, document_id=req.document_id)
    return {
        "question": req.question,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "sources": result["sources"]
    }

@router.get("/analysis/{id}")
def get_document_analysis(id: int, db: Session = Depends(get_db)):
    """Retrieves document analysis and chart metrics formatted for Chart.js."""
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_dict = doc.to_dict()
    analysis = doc_dict.get("metadata", {}).get("analysis", {})
    
    # Format for Chart.js
    element_types = analysis.get("element_types", {})
    keywords = analysis.get("word_frequency", {})

    chart_element_distribution = {
        "labels": list(element_types.keys()),
        "datasets": [
            {
                "label": "Element Count",
                "data": list(element_types.values()),
                "backgroundColor": [
                    "rgba(102, 126, 234, 0.8)",
                    "rgba(240, 147, 251, 0.8)",
                    "rgba(79, 172, 254, 0.8)",
                    "rgba(0, 242, 254, 0.8)"
                ]
            }
        ]
    }

    chart_keyword_frequency = {
        "labels": list(keywords.keys()),
        "datasets": [
            {
                "label": "Occurrences",
                "data": list(keywords.values()),
                "backgroundColor": "rgba(102, 126, 234, 0.75)",
                "borderColor": "#667eea",
                "borderWidth": 1
            }
        ]
    }

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "analysis": analysis,
        "charts": {
            "element_distribution": chart_element_distribution,
            "keyword_frequency": chart_keyword_frequency
        }
    }

@router.get("/stats/{id}")
def get_document_stats(id: int, db: Session = Depends(get_db)):
    """Retrieves document statistics summary."""
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_dict = doc.to_dict()
    analysis = doc_dict.get("metadata", {}).get("analysis", {})
    total_chars = analysis.get("total_text_length", 0)
    word_count = total_chars // 5 # Estimation
    reading_time_min = max(1, round(word_count / 200))

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "file_size": doc.file_size,
        "total_pages": analysis.get("total_pages", 1),
        "total_elements": analysis.get("total_elements", 0),
        "total_chunks": doc_dict.get("metadata", {}).get("chunks_added", 0),
        "estimated_word_count": word_count,
        "estimated_reading_time_minutes": reading_time_min,
        "upload_date": doc.upload_date.isoformat() if doc.upload_date else None
    }

