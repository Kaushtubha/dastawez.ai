from fastapi import APIRouter
from .auth import router as auth_router
from .upload import router as upload_router
from .ask import router as ask_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(upload_router, tags=["Documents"])
api_router.include_router(ask_router, tags=["Analysis & Q&A"])

__all__ = ["api_router"]

