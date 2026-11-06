import os
import time
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.db.metadata import init_db, SessionLocal, Document, DocumentChunk, User
from app.api import api_router

# OpenAPI Tags Metadata
TAGS_METADATA = [
    {
        "name": "Authentication",
        "description": "User registration, authentication, JWT session lifecycle, and profile management."
    },
    {
        "name": "Documents",
        "description": "Multi-format document ingestion (PDF, DOCX, TXT), structural element extraction, chunk storage, and catalog management."
    },
    {
        "name": "Analysis & Q&A",
        "description": "Semantic vector retrieval, LangChain/OpenAI conversational synthesis, confidence scoring, and Chart.js analytics."
    },
    {
        "name": "System",
        "description": "Health checks, runtime configuration, and platform telemetry endpoints."
    }
]

# Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on application boot
    init_db()
    yield

# Initialize FastAPI application
app = FastAPI(
    title=f"{settings.APP_NAME} Platform",
    description=(
        "**Dastawez.ai (DocuMind)** is an enterprise-grade Intelligent Document Processing (IDP) "
        "and Conversational Question-Answering platform. It features layout-preserving element "
        "extraction, spatial coordinate retention, hybrid vector search, and grounded citations."
    ),
    version="1.1.0",
    openapi_tags=TAGS_METADATA,
    contact={
        "name": "Dastawez.ai Engineering Support",
        "url": "https://github.com/Kaushtubha/dastawez.ai",
        "email": "support@dastawez.ai",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance Latency Telemetry Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response

# Standardized Error Response Exception Handlers
logger = logging.getLogger("dastawez.api")

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def custom_unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled system exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An unexpected server error occurred during request processing.",
            "detail": str(exc) if settings.DEBUG else "Internal server error",
            "status_code": 500
        }
    )

# Include API Router
app.include_router(api_router)

# Health Checks
@app.get("/health", tags=["System"])
@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.2.0"
    }

@app.get("/api/v1/system/telemetry", tags=["System"])
def system_telemetry_endpoint():
    """
    Returns platform resource telemetry, database size, storage utilization, and catalog health.
    """
    db = SessionLocal()
    try:
        total_docs = db.query(Document).count()
        total_chunks = db.query(DocumentChunk).count()
        total_users = db.query(User).count()
    finally:
        db.close()

    # Calculate upload directory size
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_bytes = 0
    if upload_dir.exists():
        for p in upload_dir.rglob("*"):
            if p.is_file():
                upload_bytes += p.stat().st_size

    # Calculate database file size if SQLite
    db_file = Path("documind.db")
    db_bytes = db_file.stat().st_size if db_file.exists() else 0

    return {
        "status": "operational",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.2.0",
        "storage": {
            "upload_directory": str(upload_dir),
            "upload_size_bytes": upload_bytes,
            "upload_size_mb": round(upload_bytes / (1024 * 1024), 2),
            "database_size_bytes": db_bytes,
            "database_size_kb": round(db_bytes / 1024, 2)
        },
        "catalog": {
            "documents_indexed": total_docs,
            "chunks_persisted": total_chunks,
            "registered_users": total_users
        }
    }

# Mount static build files if available
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets") if (static_dir / "assets").exists() else None

@app.get("/", tags=["System"])
def root_endpoint():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": f"Welcome to {settings.APP_NAME} API Gateway",
        "version": "1.1.0",
        "docs_url": "/docs",
        "api_v1": "/api/v1",
        "status": "online"
    }

@app.get("/{full_path:path}", tags=["System"])
def catch_all_spa(full_path: str):
    if full_path.startswith(("api", "docs", "redoc", "openapi.json")):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})
