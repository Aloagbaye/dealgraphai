from fastapi import FastAPI

from app.api.data import router as data_router
from app.api.health import router as health_router
from app.api.rag import router as rag_router
from app.api.search import router as search_router
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Relationship-intelligence RAG API for private capital CRM workflows.",
    version=settings.app_version,
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(data_router, prefix="/api/data", tags=["data"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(rag_router, prefix="/api/rag", tags=["rag"])
