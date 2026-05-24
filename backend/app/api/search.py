from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.services.data_loader import DataFileNotFoundError
from app.services.search_service import search_documents


router = APIRouter()


@router.get("/documents")
def search_documents_endpoint(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=10, ge=1, le=50),
    company_id: str | None = None,
    deal_id: str | None = None,
    visibility: str | None = None,
    doc_type: str | None = None,
    sector: str | None = None,
    sentiment: str | None = None,
) -> dict[str, Any]:
    try:
        return search_documents(
            query=q,
            limit=limit,
            company_id=company_id,
            deal_id=deal_id,
            visibility=visibility,
            doc_type=doc_type,
            sector=sector,
            sentiment=sentiment,
        )
    except DataFileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc