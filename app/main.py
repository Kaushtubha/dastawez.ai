import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.db.metadata import init_db
from app.api import api_router

# Initialize FastAPI application
app = FastAPI(
    title=f"{settings.APP_NAME} Platform",
    description="Intelligent Document Processing, Extraction, and RAG Q&A Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Database Startup
@app.on_event("startup")
def on_startup():
    init_db()

# Health Checks
@app.get("/health", tags=["System"])
@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0"
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
        "version": "1.0.0",
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
