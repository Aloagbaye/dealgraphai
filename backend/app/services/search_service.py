from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.services.data_loader import load_documents


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "what",
    "who",
    "with",
}


def normalize_text(text: str) -> str:
    return text.lower().strip()


def tokenize(text: str) -> list[str]:
    """
    Simple tokenizer for baseline lexical retrieval.

    This intentionally avoids external search dependencies so we can create
    a transparent retrieval baseline before adding vector search.
    """
    normalized = normalize_text(text)
    tokens = re.findall(r"[a-zA-Z0-9]+", normalized)
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def get_document_text(document: dict[str, Any]) -> str:
    title = str(document.get("title", ""))
    text = str(document.get("text", ""))
    doc_type = str(document.get("doc_type", ""))
    company_id = str(document.get("company_id", ""))
    deal_id = str(document.get("deal_id", ""))

    metadata = document.get("metadata", {})
    metadata_text = ""

    if isinstance(metadata, dict):
        metadata_text = " ".join(str(value) for value in metadata.values())

    return " ".join([title, text, doc_type, company_id, deal_id, metadata_text])


def apply_metadata_filters(
    documents: list[dict[str, Any]],
    company_id: str | None = None,
    deal_id: str | None = None,
    visibility: str | None = None,
    doc_type: str | None = None,
    sector: str | None = None,
    sentiment: str | None = None,
) -> list[dict[str, Any]]:
    filtered = documents

    if company_id:
        filtered = [
            doc for doc in filtered if str(doc.get("company_id", "")) == company_id
        ]

    if deal_id:
        filtered = [
            doc for doc in filtered if str(doc.get("deal_id", "")) == deal_id
        ]

    if visibility:
        filtered = [
            doc
            for doc in filtered
            if str(doc.get("visibility", "")).lower() == visibility.lower()
        ]

    if doc_type:
        filtered = [
            doc
            for doc in filtered
            if str(doc.get("doc_type", "")).lower() == doc_type.lower()
        ]

    if sector:
        filtered = [
            doc
            for doc in filtered
            if str(doc.get("metadata", {}).get("sector", "")).lower() == sector.lower()
        ]

    if sentiment:
        filtered = [
            doc
            for doc in filtered
            if str(doc.get("metadata", {}).get("sentiment", "")).lower()
            == sentiment.lower()
        ]

    return filtered


def score_document(query_tokens: list[str], document: dict[str, Any]) -> dict[str, Any]:
    document_text = get_document_text(document)
    document_tokens = tokenize(document_text)
    token_counts = Counter(document_tokens)

    matched_terms = [token for token in query_tokens if token in token_counts]

    if not matched_terms:
        return {
            "score": 0.0,
            "matched_terms": [],
            "match_count": 0,
            "reason": "No lexical query terms matched.",
        }

    exact_match_score = sum(token_counts[token] for token in matched_terms)
    coverage_score = len(set(matched_terms)) / max(len(set(query_tokens)), 1)

    title = normalize_text(str(document.get("title", "")))
    text = normalize_text(str(document.get("text", "")))

    title_boost = 0.0
    for token in set(matched_terms):
        if token in title:
            title_boost += 1.5

    phrase_boost = 0.0
    normalized_query = " ".join(query_tokens)

    if normalized_query and normalized_query in text:
        phrase_boost = 2.0

    score = exact_match_score + coverage_score + title_boost + phrase_boost

    return {
        "score": round(score, 4),
        "matched_terms": sorted(set(matched_terms)),
        "match_count": len(matched_terms),
        "reason": (
            f"Matched {len(set(matched_terms))} unique query terms. "
            f"Coverage={coverage_score:.2f}, title_boost={title_boost:.2f}, "
            f"phrase_boost={phrase_boost:.2f}."
        ),
    }


def build_snippet(text: str, matched_terms: list[str], max_chars: int = 320) -> str:
    if not text:
        return ""

    lowered = text.lower()

    first_match_index = None
    for term in matched_terms:
        index = lowered.find(term.lower())
        if index != -1:
            first_match_index = index
            break

    if first_match_index is None:
        return text[:max_chars] + ("..." if len(text) > max_chars else "")

    start = max(first_match_index - 80, 0)
    end = min(start + max_chars, len(text))

    snippet = text[start:end]

    if start > 0:
        snippet = "..." + snippet

    if end < len(text):
        snippet = snippet + "..."

    return snippet


def search_documents(
    query: str,
    limit: int = 10,
    company_id: str | None = None,
    deal_id: str | None = None,
    visibility: str | None = None,
    doc_type: str | None = None,
    sector: str | None = None,
    sentiment: str | None = None,
) -> dict[str, Any]:
    query_tokens = tokenize(query)

    if not query_tokens:
        return {
            "query": query,
            "query_tokens": [],
            "filters": {
                "company_id": company_id,
                "deal_id": deal_id,
                "visibility": visibility,
                "doc_type": doc_type,
                "sector": sector,
                "sentiment": sentiment,
            },
            "total_candidates": 0,
            "total_matches": 0,
            "results": [],
            "warning": "Query did not contain searchable terms.",
        }

    documents = load_documents()

    filtered_documents = apply_metadata_filters(
        documents=documents,
        company_id=company_id,
        deal_id=deal_id,
        visibility=visibility,
        doc_type=doc_type,
        sector=sector,
        sentiment=sentiment,
    )

    scored_results: list[dict[str, Any]] = []

    for document in filtered_documents:
        scoring = score_document(query_tokens, document)

        if scoring["score"] <= 0:
            continue

        text = str(document.get("text", ""))

        scored_results.append(
            {
                "doc_id": document.get("doc_id"),
                "doc_type": document.get("doc_type"),
                "title": document.get("title"),
                "date": document.get("date"),
                "company_id": document.get("company_id"),
                "deal_id": document.get("deal_id"),
                "contact_ids": document.get("contact_ids", []),
                "visibility": document.get("visibility"),
                "metadata": document.get("metadata", {}),
                "score": scoring["score"],
                "matched_terms": scoring["matched_terms"],
                "retrieval_reason": scoring["reason"],
                "snippet": build_snippet(text, scoring["matched_terms"]),
                "citation": {
                    "source_type": document.get("doc_type"),
                    "source_id": document.get("doc_id"),
                    "title": document.get("title"),
                    "date": document.get("date"),
                },
            }
        )

    scored_results.sort(
        key=lambda result: (
            result["score"],
            str(result.get("date", "")),
        ),
        reverse=True,
    )

    return {
        "query": query,
        "query_tokens": query_tokens,
        "filters": {
            "company_id": company_id,
            "deal_id": deal_id,
            "visibility": visibility,
            "doc_type": doc_type,
            "sector": sector,
            "sentiment": sentiment,
        },
        "total_candidates": len(filtered_documents),
        "total_matches": len(scored_results),
        "results": scored_results[:limit],
    }