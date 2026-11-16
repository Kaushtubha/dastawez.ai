try:
    from .metadata import (
        Base,
        engine,
        SessionLocal,
        get_db,
        init_db,
        Document,
        Chunk,
        User,
        get_documents,
        get_document_by_id,
        create_document,
        delete_document,
        create_chunk,
        get_chunks_by_document,
        create_user,
        get_user_by_email,
        get_user_by_username
    )
except ImportError:
    Base = engine = SessionLocal = get_db = init_db = None
    Document = Chunk = User = None
    get_documents = get_document_by_id = create_document = delete_document = None
    create_chunk = get_chunks_by_document = create_user = get_user_by_email = get_user_by_username = None

from .vector_store import vector_store, VectorStore

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "Document",
    "Chunk",
    "User",
    "get_documents",
    "get_document_by_id",
    "create_document",
    "delete_document",
    "create_chunk",
    "get_chunks_by_document",
    "create_user",
    "get_user_by_email",
    "get_user_by_username",
    "vector_store",
    "VectorStore"
]
