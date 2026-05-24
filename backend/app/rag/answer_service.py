from __future__ import annotations

import re
from typing import Any

from app.llm.factory import get_llm_client
from app.rag.prompt_builder import build_grounded_answer_prompt
from app.rag.schemas import RagCitation
from app.services.search_service import search_documents


def _extract_confidence(answer: str, result_count: int) -> str:
    confidence_match = re.search(
        r"Confidence:\s*(High|Medium|Low)",
        answer,
        flags=re.IGNORECASE,
    )

    if confidence_match:
        return confidence_match.group(1).title()

    if result_count >= 4:
        return "Medium"

    return "Low"


def _build_citations(results: list[dict[str, Any]]) -> list[RagCitation]:
    citations: list[RagCitation] = []

    for result in results:
        citation = result.get("citation", {})

        citations.append(
            RagCitation(
                source_id=citation.get("source_id"),
                source_type=citation.get("source_type"),
                title=citation.get("title"),
                date=citation.get("date"),
                snippet=result.get("snippet"),
                score=result.get("score"),
                matched_terms=result.get("matched_terms", []),
            )
        )

    return citations


def answer_question(
    question: str,
    limit: int = 5,
    company_id: str | None = None,
    deal_id: str | None = None,
    visibility: str | None = None,
    doc_type: str | None = None,
    sector: str | None = None,
    sentiment: str | None = None,
    llm_provider: str | None = None,
) -> dict[str, Any]:
    """Basic RAG answer flow with provider-based LLM generation."""

    warnings: list[str] = []

    search_response = search_documents(
        query=question,
        limit=limit,
        company_id=company_id,
        deal_id=deal_id,
        visibility=visibility,
        doc_type=doc_type,
        sector=sector,
        sentiment=sentiment,
    )

    results = search_response.get("results", [])

    if not results:
        warnings.append("No relevant documents were retrieved.")

    prompt = build_grounded_answer_prompt(
        question=question,
        retrieved_results=results,
    )

    llm_client = get_llm_client(llm_provider)
    llm_response = llm_client.generate(prompt)

    confidence = _extract_confidence(llm_response.text, len(results))

    return {
        "question": question,
        "answer": llm_response.text,
        "confidence": confidence,
        "llm": {
            "provider": llm_response.provider,
            "model": llm_response.model,
        },
        "retrieval_summary": {
            "query_tokens": search_response.get("query_tokens", []),
            "filters": search_response.get("filters", {}),
            "total_candidates": search_response.get("total_candidates", 0),
            "total_matches": search_response.get("total_matches", 0),
            "used_top_k": len(results),
            "prompt_preview": prompt[:1200],
        },
        "citations": _build_citations(results),
        "warnings": warnings,
    }
