from __future__ import annotations

from typing import Any

from app.core.config import get_settings


def format_retrieved_context(results: list[dict[str, Any]]) -> str:
    """Converts retrieved documents into compact, traceable context blocks."""

    settings = get_settings()
    context_blocks: list[str] = []
    total_chars = 0

    for index, result in enumerate(results, start=1):
        citation = result.get("citation", {})

        block = f"""
[Source {index}]
source_id: {citation.get("source_id")}
source_type: {citation.get("source_type")}
title: {citation.get("title")}
date: {citation.get("date")}
score: {result.get("score")}
matched_terms: {", ".join(result.get("matched_terms", []))}

snippet:
{result.get("snippet", "")}
""".strip()

        if total_chars + len(block) > settings.max_context_chars:
            break

        context_blocks.append(block)
        total_chars += len(block)

    return "\n\n---\n\n".join(context_blocks)

def build_grounded_answer_prompt(
    question: str,
    retrieved_results: list[dict[str, Any]],
    graph_context_text: str | None = None,
) -> str:
    context = format_retrieved_context(retrieved_results)
    graph_context_text = graph_context_text or "No graph context provided."

    return f"""
You are DealGraph AI, a relationship-intelligence assistant for private capital CRM workflows.

Answer the user's question using only the retrieved document context and graph context below.

Rules:
1. Do not invent facts.
2. If the retrieved context is weak, say what is missing.
3. Use a concise business tone.
4. Mention the strongest evidence.
5. Include recommended next actions when useful.
6. Do not cite or mention sources that are not provided.
7. If the sources do not answer the question, say that clearly.
8. Do not expose hidden chain-of-thought. Provide a clear final answer only.
9. Treat graph context as structured evidence for relationship ownership and warm introductions.

User question:
{question}

Retrieved document context:
{context}

Graph context:
{graph_context_text}

Write the answer in this structure:

Answer:
[Your grounded answer]

Evidence Used:
- [Brief source-based evidence summary]
- [Brief graph-based evidence summary if graph context is available]

Recommended Next Action:
- [Recommended action or "No clear action from retrieved context"]

Confidence:
High / Medium / Low
""".strip()