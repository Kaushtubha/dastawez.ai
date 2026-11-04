import pytest
from app.main import health_check
from app.api.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.db.metadata import SessionLocal, get_documents, init_db
from app.core.agent import ask_question

def test_health_check_function():
    """Verify system health endpoint response."""
    data = health_check()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["version"] == "1.0.0"

def test_auth_token_mechanisms():
    """Verify password hashing and JWT token encoding/decoding."""
    password = "SuperSecurePassword99!"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

    # Token encoding & decoding
    token = create_access_token(user_id=1, email="operator@dastawez.ai", username="operator")
    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["email"] == "operator@dastawez.ai"
    assert payload["username"] == "operator"

def test_database_and_documents():
    """Verify database initialization and document query functions."""
    init_db()
    db = SessionLocal()
    try:
        docs = get_documents(db)
        assert isinstance(docs, list)
        if len(docs) > 0:
            doc_dict = docs[0].to_dict()
            assert "filename" in doc_dict
            assert "file_type" in doc_dict
    finally:
        db.close()

def test_agent_qa_pipeline():
    """Verify document QA pipeline and attribution."""
    db = SessionLocal()
    try:
        response = ask_question(db=db, question="What is in this document?")
        assert "answer" in response
        assert "confidence" in response
        assert "sources" in response
        assert isinstance(response["confidence"], float)
        assert isinstance(response["sources"], list)
    finally:
        db.close()
