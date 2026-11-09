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
    version="1.3.2",
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

# In-Memory Token Bucket Rate Limiter
RATE_LIMIT_MAX = 300  # requests per minute per client IP
RATE_LIMIT_WINDOW = 60.0  # seconds
_client_request_history = {}

@app.middleware("http")
async def rate_limiter_middleware(request: Request, call_next):
    # Bypass for static assets and documentation
    path = request.url.path
    if path.startswith(("/assets", "/docs", "/redoc", "/openapi.json")):
        return await call_next(request)

    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()

    # Clean requests older than the sliding window
    reqs = [t for t in _client_request_history.get(client_ip, []) if now - t < RATE_LIMIT_WINDOW]
    if len(reqs) >= RATE_LIMIT_MAX:
        return JSONResponse(
            status_code=429,
            content={
                "error": True,
                "message": "Rate limit exceeded. Too many requests. Please wait a moment.",
                "detail": f"Max {RATE_LIMIT_MAX} requests per minute limit reached.",
                "status_code": 429
            },
            headers={"Retry-After": "60", "X-RateLimit-Limit": str(RATE_LIMIT_MAX), "X-RateLimit-Remaining": "0"}
        )

    reqs.append(now)
    _client_request_history[client_ip] = reqs

    response = await call_next(request)
    remaining = max(0, RATE_LIMIT_MAX - len(reqs))
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
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
        "version": "1.3.2"
    }

@app.get("/api/v1/system/health/detailed", tags=["System"])
def detailed_health_check():
    """
    Kubernetes-ready liveness/readiness probe and runtime diagnostics endpoint.
    Performs live database connectivity latency check and vector store status probing.
    """
    import sys
    import platform
    from datetime import datetime, timezone
    from sqlalchemy import text
    from app.db.vector_store import HAS_QDRANT

    # Database connectivity probe & latency measurement
    db_start = time.perf_counter()
    db_ok = False
    db_latency_ms = None
    db_err = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_latency_ms = round((time.perf_counter() - db_start) * 1000, 2)
        db_ok = True
    except Exception as e:
        db_err = str(e)

    overall_status = "ready" if db_ok else "degraded"

    return {
        "status": overall_status,
        "app": settings.APP_NAME,
        "version": "1.3.2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "probes": {
            "liveness": "passing",
            "readiness": "passing" if db_ok else "failing",
            "database": {
                "status": "healthy" if db_ok else "unhealthy",
                "latency_ms": db_latency_ms,
                "error": db_err
            },
            "vector_store": {
                "status": "connected" if HAS_QDRANT else "fallback_local",
                "engine": "Qdrant Vector DB" if HAS_QDRANT else "TF-IDF Vectorizer"
            }
        },
        "system": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "environment": settings.APP_ENV
        }
    }

@app.get("/api/v1/system/capabilities", tags=["System"])
def system_capabilities_endpoint():
    """
    Exposes platform parsing capabilities, allowed extensions, vector store configuration, and AI model parameters.
    """
    from app.db.vector_store import HAS_QDRANT
    return {
        "app_name": settings.APP_NAME,
        "version": "1.3.2",
        "supported_formats": sorted(list(settings.ALLOWED_EXTENSIONS)),
        "max_upload_size_bytes": settings.MAX_UPLOAD_SIZE,
        "max_upload_size_mb": settings.MAX_UPLOAD_SIZE // (1024 * 1024),
        "vector_search": {
            "primary_engine": "Qdrant Vector DB" if HAS_QDRANT else "Local TF-IDF Vectorizer",
            "qdrant_connected": HAS_QDRANT,
            "embedding_model": settings.EMBEDDING_MODEL
        },
        "ai_synthesis": {
            "llm_model": settings.OPENAI_MODEL,
            "has_openai_key": bool(settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("your-")),
            "fallback_mode": "Local Grounded Extractive Synthesis"
        },
        "features": {
            "sha256_deduplication": True,
            "batch_deletion": True,
            "archive_zip_export": True,
            "markdown_parser": True,
            "rate_limiting": True,
            "executive_summaries": True,
            "detailed_health_probe": True,
            "hierarchical_chunking": True
        }
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
        "version": "1.3.2",
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
