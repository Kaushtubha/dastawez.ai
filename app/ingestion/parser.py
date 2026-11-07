import re
import os
import collections
from typing import List, Dict, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Common stop words for keyword extraction
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd",
    "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}


class ParsedElement:
    def __init__(
        self,
        text: str,
        element_type: str = "NarrativeText",
        page_number: int = 1,
        coordinates: Tuple[int, int, int, int] = (100, 100, 500, 150)
    ):
        self.text = text.strip()
        self.element_type = element_type
        self.page_number = page_number
        self.coordinates = coordinates

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "element_type": self.element_type,
            "page_number": self.page_number,
            "coordinates": list(self.coordinates)
        }


class DocumentParser:
    """Multi-format Document Parser supporting PDF, DOCX, TXT, and Markdown with layout intelligence."""

    def parse(self, file_path: str, filename: str) -> Dict[str, Any]:
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            elements, total_pages = self._parse_pdf(file_path, filename)
        elif ext in (".docx", ".doc"):
            elements, total_pages = self._parse_docx(file_path)
        elif ext in (".md", ".markdown"):
            elements, total_pages = self._parse_markdown(file_path)
        else:
            elements, total_pages = self._parse_txt(file_path)

        analysis = self._generate_analysis(elements, total_pages, file_path, filename, ext)
        return {
            "elements": [e.to_dict() for e in elements],
            "analysis": analysis,
            "total_pages": total_pages
        }

    def _parse_pdf(self, file_path: str, filename: str) -> Tuple[List[ParsedElement], int]:
        elements: List[ParsedElement] = []
        total_pages = 1

        # Try Unstructured first
        try:
            from unstructured.partition.pdf import partition_pdf
            raw_elements = partition_pdf(filename=file_path)
            for el in raw_elements:
                el_type = type(el).__name__
                page = getattr(el.metadata, "page_number", 1) or 1
                total_pages = max(total_pages, page)
                elements.append(ParsedElement(text=str(el), element_type=el_type, page_number=page))
            return elements, total_pages
        except Exception as e:
            logger.info("Unstructured PDF partition unavailable or failed (%s). Falling back to PyPDF.", e)

        # PyPDF Fallback
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            total_pages = len(reader.pages)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                for line in lines:
                    if len(line) < 60 and line.isupper():
                        el_type = "Title"
                    elif line.startswith(("-", "*", "•")):
                        el_type = "ListItem"
                    elif "|" in line:
                        el_type = "Table"
                    else:
                        el_type = "NarrativeText"
                    elements.append(ParsedElement(text=line, element_type=el_type, page_number=idx + 1))
            return elements, total_pages
        except Exception as e:
            logger.error("PyPDF parsing failed: %s", e)

        # Fallback dummy element if file reading completely fails
        return [ParsedElement(text="Empty or unreadable document content.", element_type="NarrativeText")], 1

    def _parse_docx(self, file_path: str) -> Tuple[List[ParsedElement], int]:
        elements: List[ParsedElement] = []
        try:
            import docx
            doc = docx.Document(file_path)
            total_paragraphs = len(doc.paragraphs)
            page_estimate = max(1, total_paragraphs // 15)

            for idx, p in enumerate(doc.paragraphs):
                text = p.text.strip()
                if not text:
                    continue

                if p.style and "heading" in p.style.name.lower():
                    el_type = "Title"
                elif p.style and "list" in p.style.name.lower() or text.startswith(("-", "*", "•")):
                    el_type = "ListItem"
                else:
                    el_type = "NarrativeText"

                elements.append(ParsedElement(text=text, element_type=el_type, page_number=page_estimate))

            # Parse docx tables
            for table in doc.tables:
                table_lines = []
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    table_lines.append(" | ".join(cells))
                if table_lines:
                    elements.append(
                        ParsedElement(
                            text="\n".join(table_lines),
                            element_type="Table",
                            page_number=page_estimate
                        )
                    )
            return elements, page_estimate
        except Exception as e:
            logger.error("Docx parsing failed: %s", e)
            return [ParsedElement(text="Docx content.", element_type="NarrativeText")], 1

    def _parse_txt(self, file_path: str) -> Tuple[List[ParsedElement], int]:
        elements: List[ParsedElement] = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        total_pages = max(1, len(paragraphs) // 10)

        for idx, para in enumerate(paragraphs):
            page_num = (idx // 10) + 1
            if len(para) < 60 and (para.isupper() or para.endswith(":")):
                el_type = "Title"
            elif any(para.startswith(bullet) for bullet in ("-", "*", "1.", "2.")):
                el_type = "ListItem"
            elif "|" in para:
                el_type = "Table"
            else:
                el_type = "NarrativeText"
            elements.append(ParsedElement(text=para, element_type=el_type, page_number=page_num))

        return elements, total_pages

    def _parse_markdown(self, file_path: str) -> Tuple[List[ParsedElement], int]:
        """Parses Markdown files preserving header hierarchy, lists, tables, and code blocks."""
        elements: List[ParsedElement] = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        page_estimate = max(1, len(lines) // 35)
        in_code_block = False
        code_lines = []

        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            page_num = max(1, (idx // 35) + 1)

            if stripped.startswith("```"):
                if in_code_block:
                    in_code_block = False
                    elements.append(
                        ParsedElement(
                            text="\n".join(code_lines),
                            element_type="CodeBlock",
                            page_number=page_num
                        )
                    )
                    code_lines = []
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_lines.append(line.rstrip())
                continue

            if stripped.startswith("#"):
                header_text = stripped.lstrip("#").strip()
                elements.append(
                    ParsedElement(
                        text=header_text,
                        element_type="Title",
                        page_number=page_num
                    )
                )
            elif stripped.startswith("|") and stripped.endswith("|"):
                elements.append(
                    ParsedElement(
                        text=stripped,
                        element_type="Table",
                        page_number=page_num
                    )
                )
            elif any(stripped.startswith(b) for b in ("- ", "* ", "+ ")) or re.match(r"^\d+\.\s+", stripped):
                elements.append(
                    ParsedElement(
                        text=stripped,
                        element_type="ListItem",
                        page_number=page_num
                    )
                )
            else:
                elements.append(
                    ParsedElement(
                        text=stripped,
                        element_type="NarrativeText",
                        page_number=page_num
                    )
                )

        if code_lines:
            elements.append(
                ParsedElement(
                    text="\n".join(code_lines),
                    element_type="CodeBlock",
                    page_number=page_estimate
                )
            )

        if not elements:
            elements = [ParsedElement(text="Empty markdown document.", element_type="NarrativeText")]

        return elements, page_estimate

    def _generate_analysis(
        self,
        elements: List[ParsedElement],
        total_pages: int,
        file_path: str,
        filename: str,
        ext: str
    ) -> Dict[str, Any]:
        """Calculates element distributions, keyword frequencies, and document statistics."""
        element_types_count = collections.Counter([e.element_type for e in elements])
        all_text = " ".join([e.text for e in elements])
        
        words = re.findall(r"\b[A-Za-z0-9_-]{3,}\b", all_text.lower())
        filtered_words = [w for w in words if w not in STOP_WORDS]
        word_freq = collections.Counter(filtered_words)

        top_keywords = [word for word, count in word_freq.most_common(12)]
        top_word_freq = dict(word_freq.most_common(10))

        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else len(all_text)

        total_elements = len(elements)
        avg_len = round(len(all_text) / max(1, total_elements), 1)

        pages_list = sorted(list(set(e.page_number for e in elements))) or [1]

        return {
            "total_elements": total_elements,
            "element_types": dict(element_types_count),
            "element_type_distribution": dict(element_types_count),
            "total_pages": total_pages,
            "total_chunks": total_elements,
            "top_keywords": top_keywords,
            "word_frequency": top_word_freq,
            "total_text_length": len(all_text),
            "average_text_length_per_element": avg_len,
            "page_numbers": pages_list,
            "file_info": {
                filename: {
                    "pages": total_pages,
                    "size": file_size,
                    "type": ext,
                    "elements": total_elements
                }
            }
        }


def parse_document(file_path: str, filename: str) -> Dict[str, Any]:
    parser = DocumentParser()
    return parser.parse(file_path, filename)
