import json
from datetime import datetime
from typing import Generator, List, Optional, Dict, Any
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    func
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from app.config import settings

# Database Engine & Session
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DB_ECHO
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="processed")
    checksum_sha256 = Column(String(64), nullable=True, index=True)
    processing_duration_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        meta = {}
        if self.metadata_json:
            try:
                meta = json.loads(self.metadata_json)
            except Exception:
                meta = {}
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "status": self.status,
            "checksum_sha256": self.checksum_sha256,
            "processing_duration_ms": self.processing_duration_ms,
            "error_message": self.error_message,
            "metadata": meta
        }


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_metadata_json = Column(Text, nullable=True)

    document = relationship("Document", back_populates="chunks")

    def to_dict(self) -> Dict[str, Any]:
        meta = {}
        if self.chunk_metadata_json:
            try:
                meta = json.loads(self.chunk_metadata_json)
            except Exception:
                meta = {}
        return {
            "id": self.id,
            "document_id": self.document_id,
            "chunk_text": self.chunk_text,
            "metadata": meta
        }


# Model alias for enterprise telemetry
DocumentChunk = Chunk


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active
        }


def init_db():
    """Initializes tables in the database and applies non-destructive schema migrations."""
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            cursor = conn.connection.cursor()
            cursor.execute("PRAGMA table_info(documents);")
            columns = [row[1] for row in cursor.fetchall()]

            if "checksum_sha256" not in columns:
                cursor.execute("ALTER TABLE documents ADD COLUMN checksum_sha256 VARCHAR(64);")
            if "processing_duration_ms" not in columns:
                cursor.execute("ALTER TABLE documents ADD COLUMN processing_duration_ms INTEGER;")
            if "error_message" not in columns:
                cursor.execute("ALTER TABLE documents ADD COLUMN error_message TEXT;")
            conn.connection.commit()
    except Exception as e:
        print(f"Schema migration note: {e}")
    print("Database tables initialized successfully.")


def get_db() -> Generator[Session, None, None]:
    """Dependency helper for route handlers to access the DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database Queries and Helpers
def get_documents(db: Session, skip: int = 0, limit: int = 100) -> List[Document]:
    return db.query(Document).order_by(Document.id.desc()).offset(skip).limit(limit).all()


def get_document_by_id(db: Session, doc_id: int) -> Optional[Document]:
    return db.query(Document).filter(Document.id == doc_id).first()


def get_document_by_hash(db: Session, checksum_sha256: str) -> Optional[Document]:
    return db.query(Document).filter(Document.checksum_sha256 == checksum_sha256).first()


def create_document(
    db: Session,
    filename: str,
    file_path: str,
    file_type: str,
    file_size: int,
    metadata_json: Optional[str] = None,
    checksum_sha256: Optional[str] = None,
    processing_duration_ms: Optional[int] = None,
    error_message: Optional[str] = None,
    status: str = "processed"
) -> Document:
    doc = Document(
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        metadata_json=metadata_json,
        checksum_sha256=checksum_sha256,
        processing_duration_ms=processing_duration_ms,
        error_message=error_message,
        status=status
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, doc_id: int) -> bool:
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True


def create_chunk(
    db: Session,
    document_id: int,
    chunk_text: str,
    chunk_metadata_json: Optional[str] = None
) -> Chunk:
    chunk = Chunk(
        document_id=document_id,
        chunk_text=chunk_text,
        chunk_metadata_json=chunk_metadata_json
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk


def get_chunks_by_document(db: Session, document_id: int) -> List[Chunk]:
    return db.query(Chunk).filter(Chunk.document_id == document_id).all()


# User Query Helpers
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, email: str, hashed_password: str) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Auto-initialize database tables and schema migrations on module import
init_db()

