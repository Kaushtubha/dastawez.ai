from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.db.metadata import get_db, get_document_by_id, get_documents
from app.core.agent import ask_question

router = APIRouter()

class SourceCitation(BaseModel):
    chunk_id: Optional[int] = None
    filename: str
    page_number: int
    element_type: str
    score: float
    excerpt: str

class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=1500,
        description="The natural language question to ask against document context.",
        examples=["What are the termination clauses in this agreement?"]
    )
    document_id: Optional[int] = Field(
        None,
        gt=0,
        description="Optional unique identifier of the document to scope the query."
    )

    @field_validator("question")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Question cannot be blank or contain only whitespace.")
        return clean

class AskResponse(BaseModel):
    question: str
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Calculated confidence score between 0.0 and 1.0.")
    sources: List[Dict[str, Any]]

@router.post("/ask", response_model=AskResponse, summary="Query Document Context")
def ask_document_endpoint(
    req: AskRequest,
    db: Session = Depends(get_db)
):
    """
    Submits a natural language query against indexed document chunks.
    Returns synthesized answer, attribution citations, and confidence scoring.
    """
    if req.document_id:
        doc = get_document_by_id(db, req.document_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {req.document_id} not found."
            )

    result = ask_question(db=db, question=req.question, document_id=req.document_id)
    return {
        "question": req.question,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "sources": result["sources"]
    }

@router.get("/analysis/{id}", summary="Get Document Analysis for Chart.js")
def get_document_analysis(id: int, db: Session = Depends(get_db)):
    """Retrieves document analysis and chart metrics formatted for Chart.js."""
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    doc_dict = doc.to_dict()
    analysis = doc_dict.get("metadata", {}).get("analysis", {})
    
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

@router.get("/stats/{id}", summary="Get Document Summary Statistics")
def get_document_stats(id: int, db: Session = Depends(get_db)):
    """Retrieves document statistics summary."""
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    doc_dict = doc.to_dict()
    analysis = doc_dict.get("metadata", {}).get("analysis", {})
    total_chars = analysis.get("total_text_length", 0)
    word_count = total_chars // 5
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

@router.get("/documents/{id}/summary", summary="Generate Automated Executive Document Summary")
def get_document_executive_summary(id: int, db: Session = Depends(get_db)):
    """
    Synthesizes an automated executive summary and highlights for an ingested document.
    """
    doc = get_document_by_id(db, id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {id} not found."
        )

    doc_dict = doc.to_dict()
    meta = doc_dict.get("metadata", {})
    analysis = meta.get("analysis", {})
    chunks = meta.get("chunks", [])
    keywords = list(analysis.get("word_frequency", {}).keys())[:6]

    total_chars = analysis.get("total_text_length", 0)
    word_count = total_chars // 5
    reading_time = max(1, round(word_count / 200))
    element_types = analysis.get("element_types", {})

    # Generate synthesis highlights from initial chunks
    highlights = []
    for c in chunks[:5]:
        txt = (c.get("text") or c.get("content") or "").strip()
        if txt and len(txt) > 20:
            snippet = txt[:160] + "..." if len(txt) > 160 else txt
            highlights.append(snippet)

    if not highlights:
        highlights = [f"Processed document containing {analysis.get('total_elements', 0)} layout elements across {analysis.get('total_pages', 1)} page(s)."]

    exec_summary = (
        f"Document '{doc.filename}' ({doc.file_type or 'unspecified'}) comprises "
        f"{analysis.get('total_pages', 1)} page(s) and {analysis.get('total_elements', 0)} parsed layout elements. "
        f"Primary structural elements include: {', '.join(f'{k} ({v})' for k, v in element_types.items()) or 'standard text blocks'}. "
        f"Estimated content volume is approximately {word_count} words (~{reading_time} min read)."
    )

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "executive_summary": exec_summary,
        "key_takeaways": highlights,
        "key_topics": keywords,
        "metrics": {
            "total_pages": analysis.get("total_pages", 1),
            "total_elements": analysis.get("total_elements", 0),
            "total_chunks": len(chunks),
            "estimated_word_count": word_count,
            "estimated_reading_time_minutes": reading_time
        }
    }

