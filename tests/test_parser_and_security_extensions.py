import os
import tempfile
import pytest
from app.ingestion.parser import DocumentParser
from app.config import Settings


def test_magic_bytes_valid_rtf():
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".rtf") as f:
        f.write(b"{\\rtf1\\ansi\\deff0 {\\fonttbl{\\f0 Arial;}}\\fs20 Hello RTF document}")
        path = f.name
    try:
        is_valid, reason = DocumentParser.validate_magic_bytes(path, "doc.rtf")
        assert is_valid is True
        assert reason == "valid_rtf"
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_magic_bytes_invalid_rtf():
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".rtf") as f:
        f.write(b"NOT_AN_RTF_FILE")
        path = f.name
    try:
        is_valid, reason = DocumentParser.validate_magic_bytes(path, "corrupt.rtf")
        assert is_valid is False
        assert "Missing" in reason or "Invalid" in reason
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_rtf_parsing_content_extraction():
    parser = DocumentParser()
    sample_rtf = (
        "{\\rtf1\\ansi\\deff0\n"
        "{\\fonttbl{\\f0 Times New Roman;}}\n"
        "\\b LEGAL NOTICE \\b0\\par\n"
        "This is an automated legal disclosure text.\\par\n"
        "\\i Second clause of agreement.\\i0\\par\n"
        "}"
    )
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".rtf") as f:
        f.write(sample_rtf)
        path = f.name
    try:
        res = parser.parse(path, "contract.rtf")
        assert "elements" in res
        elements = res["elements"]
        assert len(elements) >= 2
        combined_text = " ".join(e["text"] for e in elements)
        assert "LEGAL NOTICE" in combined_text
        assert "automated legal disclosure text" in combined_text
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_allowed_hosts_configuration_parsing():
    s = Settings()
    assert isinstance(s.ALLOWED_HOSTS, list)
    assert len(s.ALLOWED_HOSTS) >= 1
