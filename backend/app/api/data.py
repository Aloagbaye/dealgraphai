from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.services.data_loader import (
    DataFileNotFoundError,
    load_companies,
    load_contacts,
    load_deals,
    load_documents,
    load_eval_questions,
    load_interactions,
    load_relationship_edges,
    load_schema_markdown,
    load_dataset_summary,
)


router = APIRouter()


def _limit_records(records: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return records[:limit]


def _safe_load(loader):
    try:
        return loader()
    except DataFileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/summary")
def get_dataset_summary() -> dict[str, Any]:
    return _safe_load(load_dataset_summary)


@router.get("/companies")
def get_companies(
    limit: int = Query(default=20, ge=1, le=500),
) -> list[dict[str, Any]]:
    records = _safe_load(load_companies)
    return _limit_records(records, limit)


@router.get("/contacts")
def get_contacts(
    limit: int = Query(default=20, ge=1, le=500),
    company_id: str | None = None,
) -> list[dict[str, Any]]:
    records = _safe_load(load_contacts)

    if company_id:
        records = [record for record in records if record.get("company_id") == company_id]

    return _limit_records(records, limit)


@router.get("/deals")
def get_deals(
    limit: int = Query(default=20, ge=1, le=500),
    company_id: str | None = None,
    stage: str | None = None,
) -> list[dict[str, Any]]:
    records = _safe_load(load_deals)

    if company_id:
        records = [record for record in records if record.get("company_id") == company_id]

    if stage:
        records = [
            record
            for record in records
            if str(record.get("stage", "")).lower() == stage.lower()
        ]

    return _limit_records(records, limit)


@router.get("/interactions")
def get_interactions(
    limit: int = Query(default=20, ge=1, le=500),
    company_id: str | None = None,
    deal_id: str | None = None,
    source_type: str | None = None,
) -> list[dict[str, Any]]:
    records = _safe_load(load_interactions)

    if company_id:
        records = [record for record in records if record.get("company_id") == company_id]

    if deal_id:
        records = [record for record in records if record.get("deal_id") == deal_id]

    if source_type:
        records = [
            record
            for record in records
            if str(record.get("source_type", record.get("type", ""))).lower()
            == source_type.lower()
        ]

    return _limit_records(records, limit)


@router.get("/relationships")
def get_relationships(
    limit: int = Query(default=20, ge=1, le=500),
    from_id: str | None = None,
    to_id: str | None = None,
) -> list[dict[str, Any]]:
    records = _safe_load(load_relationship_edges)

    if from_id:
        records = [record for record in records if record.get("from_id") == from_id]

    if to_id:
        records = [record for record in records if record.get("to_id") == to_id]

    return _limit_records(records, limit)


@router.get("/documents")
def get_documents(
    limit: int = Query(default=20, ge=1, le=500),
    company_id: str | None = None,
    deal_id: str | None = None,
    visibility: str | None = None,
    doc_type: str | None = None,
) -> list[dict[str, Any]]:
    records = _safe_load(load_documents)

    if company_id:
        records = [record for record in records if record.get("company_id") == company_id]

    if deal_id:
        records = [record for record in records if record.get("deal_id") == deal_id]

    if visibility:
        records = [
            record
            for record in records
            if str(record.get("visibility", "")).lower() == visibility.lower()
        ]

    if doc_type:
        records = [
            record
            for record in records
            if str(record.get("doc_type", "")).lower() == doc_type.lower()
        ]

    return _limit_records(records, limit)


@router.get("/eval-questions")
def get_eval_questions(
    limit: int = Query(default=20, ge=1, le=500),
    intent: str | None = None,
) -> list[dict[str, Any]]:
    records = _safe_load(load_eval_questions)

    if intent:
        records = [
            record
            for record in records
            if str(record.get("intent", "")).lower() == intent.lower()
        ]

    return _limit_records(records, limit)


@router.get("/schema")
def get_schema() -> dict[str, str]:
    schema = _safe_load(load_schema_markdown)
    return {"schema_markdown": schema}