import re
from typing import Dict, Any, List, Tuple

class Guardrails:
    """Security, input sanitation, prompt injection defense, PII redaction, and response confidence scoring."""

    # Common prompt injection, override, and jailbreak signatures
    PROMPT_INJECTION_PATTERNS = [
        (re.compile(r"(?i)\bignore\s+(all\s+|any\s+|the\s+)?(previous|prior|above)\s+(instructions|prompts|directives)\b"), "instruction_override"),
        (re.compile(r"(?i)\b(system\s+prompt|developer\s+mode|jailbreak|dan\s+mode)\b"), "jailbreak_attempt"),
        (re.compile(r"(?i)\b(you\s+are\s+now|act\s+as\s+an?\s+unrestricted|bypass\s+all\s+rules)\b"), "persona_hijacking"),
        (re.compile(r"(?i)\b(reveal|leak|print|show)\s+(the\s+)?(system|initial|hidden)\s+(instructions|prompt|rules)\b"), "prompt_leakage"),
        (re.compile(r"(?i)\b(union\s+select|drop\s+table|delete\s+from|insert\s+into)\b"), "sql_injection")
    ]

    # Regex patterns for identifying sensitive PII
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
    CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
    API_KEY_PATTERN = re.compile(r"\b(?:sk-[a-zA-Z0-9_-]{20,}|ghp_[a-zA-Z0-9_-]{20,})\b")

    @classmethod
    def detect_prompt_injection(cls, query: str) -> Tuple[bool, str]:
        """
        Inspects query string for known adversarial injection or prompt hijacking patterns.
        Returns (is_detected, reason_code).
        """
        if not query:
            return False, ""
        for pattern, reason in cls.PROMPT_INJECTION_PATTERNS:
            if pattern.search(query):
                return True, reason
        return False, ""

    @classmethod
    def redact_pii(cls, text: str) -> str:
        """
        Redacts emails, phone numbers, credit cards, and API secrets from text.
        """
        if not text:
            return ""
        clean = cls.API_KEY_PATTERN.sub("[REDACTED_KEY]", text)
        clean = cls.CARD_PATTERN.sub("[REDACTED_CARD]", clean)
        clean = cls.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", clean)
        clean = cls.PHONE_PATTERN.sub("[REDACTED_PHONE]", clean)
        return clean

    @staticmethod
    def sanitize_input(text: str) -> str:
        if not text:
            return ""
        # Remove null bytes and excessive whitespace
        clean = text.replace("\x00", "").strip()
        clean = re.sub(r"\s+", " ", clean)
        return clean[:1000] # Limit query length

    @staticmethod
    def calculate_confidence(
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        generated_answer: str
    ) -> float:
        if not retrieved_chunks:
            return 0.25

        # Top vector score
        best_score = retrieved_chunks[0].get("score", 0.5)

        # Keyword overlap between answer and retrieved text
        retrieved_combined = " ".join(c.get("chunk_text", "") for c in retrieved_chunks).lower()
        query_words = set(re.findall(r"\w{3,}", query.lower()))
        answer_words = set(re.findall(r"\w{3,}", generated_answer.lower()))

        query_in_context = len(query_words.intersection(set(re.findall(r"\w{3,}", retrieved_combined))))
        overlap_ratio = query_in_context / max(1, len(query_words))

        base_conf = 0.5 + (best_score * 0.3) + (overlap_ratio * 0.15)
        # Clamp between 0.35 and 0.98
        return round(min(0.98, max(0.35, base_conf)), 2)

    @staticmethod
    def format_sources(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = []
        seen_refs = set()
        for c in retrieved_chunks:
            meta = c.get("metadata", {})
            filename = meta.get("filename", f"Document #{c.get('document_id', 1)}")
            page = meta.get("page_number", 1)
            el_type = meta.get("element_type", "NarrativeText")
            ref_key = f"{filename}_{page}"
            
            if ref_key not in seen_refs:
                seen_refs.add(ref_key)
                excerpt = c.get("chunk_text", "")[:160] + "..." if len(c.get("chunk_text", "")) > 160 else c.get("chunk_text", "")
                sources.append({
                    "chunk_id": c.get("id"),
                    "filename": filename,
                    "page_number": page,
                    "element_type": el_type,
                    "score": c.get("score", 0.8),
                    "excerpt": excerpt
                })
        return sources

