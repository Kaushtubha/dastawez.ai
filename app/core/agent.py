import re
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.core.retriever import context_retriever
from app.core.guardrails import Guardrails

logger = logging.getLogger(__name__)

class AIAgent:
    """Document Q&A Intelligence Agent supporting OpenAI and local synthesis."""

    def __init__(self):
        self.openai_client = None
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("your-"):
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized with model %s", settings.OPENAI_MODEL)
            except Exception as e:
                logger.warning("Could not initialize OpenAI client: %s", e)

    def ask(
        self,
        db: Session,
        question: str,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        sanitized_query = Guardrails.sanitize_input(question)
        if not sanitized_query:
            return {
                "answer": "Please provide a valid question.",
                "confidence": 0.0,
                "sources": []
            }

        # 1. Retrieve most relevant context chunks
        chunks = context_retriever.retrieve(
            db=db,
            query=sanitized_query,
            document_id=document_id,
            top_k=4
        )

        if not chunks:
            return {
                "answer": "No relevant document context found. Please ensure documents have been uploaded and processed.",
                "confidence": 0.20,
                "sources": []
            }

        # 2. Try LLM Generation if OpenAI is available
        if self.openai_client:
            try:
                context_block = "\n\n".join(
                    f"[Source: {c.get('metadata', {}).get('filename', 'doc')} | Page {c.get('metadata', {}).get('page_number', 1)}]:\n{c.get('chunk_text', '')}"
                    for c in chunks
                )
                prompt = (
                    "You are Dastawez.ai (DocuMind), an enterprise document intelligence assistant. "
                    "Answer the user question using ONLY the provided document context below. "
                    "If the answer is not contained in the context, explicitly say so. "
                    "Be accurate, concise, and professional.\n\n"
                    f"Context:\n{context_block}\n\n"
                    f"Question: {sanitized_query}\nAnswer:"
                )
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an intelligent document analysis engine."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=600
                )
                answer_text = response.choices[0].message.content.strip()
                confidence = Guardrails.calculate_confidence(sanitized_query, chunks, answer_text)
                sources = Guardrails.format_sources(chunks)
                return {
                    "answer": answer_text,
                    "confidence": confidence,
                    "sources": sources
                }
            except Exception as e:
                logger.warning("OpenAI generation failed (%s), falling back to local synthesis.", e)

        # 3. High-Quality Local Context Synthesis
        answer_text = self._synthesize_local_answer(sanitized_query, chunks)
        confidence = Guardrails.calculate_confidence(sanitized_query, chunks, answer_text)
        sources = Guardrails.format_sources(chunks)

        return {
            "answer": answer_text,
            "confidence": confidence,
            "sources": sources
        }

    def _synthesize_local_answer(self, query: str, chunks: list) -> str:
        """Synthesizes an intelligent, structured response directly from retrieved chunks."""
        query_words = [w.lower() for w in re.findall(r"\b\w{3,}\b", query)]
        sentences_with_scores = []

        for c in chunks:
            text = c.get("chunk_text", "")
            # Split into sentences
            sentences = re.split(r"(?<=[.!?])\s+", text)
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) < 15:
                    continue
                s_lower = s_clean.lower()
                matches = sum(1 for w in query_words if w in s_lower)
                if matches > 0:
                    sentences_with_scores.append((matches, s_clean, c.get("metadata", {}).get("page_number", 1)))

        if sentences_with_scores:
            # Sort sentences by match quality
            sentences_with_scores.sort(key=lambda x: x[0], reverse=True)
            top_sentences = sentences_with_scores[:4]
            points = []
            for _, sentence, page in top_sentences:
                points.append(f"• {sentence} *(Ref: Page {page})*")
            return (
                f"Based on the analysis of the document context, here is what was found:\n\n"
                + "\n\n".join(points)
            )

        # Fallback summary of top chunks
        primary_chunk = chunks[0].get("chunk_text", "")
        preview = primary_chunk[:350].strip() + "..."
        page = chunks[0].get("metadata", {}).get("page_number", 1)
        return (
            f"According to the document records (Page {page}), relevant sections indicate:\n\n"
            f"> \"{preview}\"\n\n"
            f"You can explore related details in the document analysis dashboard."
        )


ai_agent = AIAgent()

def ask_question(db: Session, question: str, document_id: Optional[int] = None) -> Dict[str, Any]:
    return ai_agent.ask(db, question, document_id)

