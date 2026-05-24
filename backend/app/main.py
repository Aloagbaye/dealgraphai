from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.data import router as data_router


app = FastAPI(
    title="DealGraph AI API",
    description="Relationship-intelligence RAG API for private capital CRM workflows.",
    version="0.2.0",
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(data_router, prefix="/api/data", tags=["data"])