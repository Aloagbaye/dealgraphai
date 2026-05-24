from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RagAnswerRequest(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=15)

    company_id: str | None = None
    deal_id: str | None = None
    visibility: str | None = None
    doc_type: str | None = None
    sector: str | None = None
    sentiment: str | None = None

    # Supported values: mock, openai, anthropic.
    # If omitted, backend/.env LLM_PROVIDER is used.
    llm_provider: str | None = None


class RagCitation(BaseModel):
    source_id: str | None = None
    source_type: str | None = None
    title: str | None = None
    date: str | None = None
    snippet: str | None = None
    score: float | None = None
    matched_terms: list[str] = Field(default_factory=list)


class RagAnswerResponse(BaseModel):
    question: str
    answer: str
    confidence: str
    llm: dict[str, Any]
    retrieval_summary: dict[str, Any]
    citations: list[RagCitation]
    warnings: list[str] = Field(default_factory=list)
