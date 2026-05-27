from __future__ import annotations

from typing import Any

from app.services.graph_service import get_graph_service


def build_graph_context(
    company_id: str | None = None,
    contact_id: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    graph = get_graph_service()

    context: dict[str, Any] = {
        "included": False,
        "company_relationships": [],
        "contact_relationships": [],
    }

    if company_id:
        context["company_relationships"] = graph.strongest_relationships_for_company(
            company_id=company_id,
            limit=limit,
        )
        context["included"] = True

    if contact_id:
        context["contact_relationships"] = graph.strongest_relationships_for_contact(
            contact_id=contact_id,
            limit=limit,
        )
        context["included"] = True

    return context


def format_graph_context_for_prompt(graph_context: dict[str, Any]) -> str:
    if not graph_context.get("included"):
        return "No graph context provided."

    lines = []

    company_relationships = graph_context.get("company_relationships", [])

    if company_relationships:
        lines.append("Strongest company relationships:")

        for item in company_relationships:
            contact = item.get("contact", {})
            owner = item.get("relationship_owner", {})

            lines.append(
                "- "
                f"Contact: {contact.get('name')} ({contact.get('title')}); "
                f"Owner: {owner.get('name')}; "
                f"Strength: {contact.get('relationship_strength')}; "
                f"Interactions: {contact.get('interaction_count')}; "
                f"Last interaction: {contact.get('last_interaction')}; "
                f"Score: {item.get('score')}"
            )

    contact_relationships = graph_context.get("contact_relationships", [])

    if contact_relationships:
        lines.append("Strongest contact relationships:")

        for item in contact_relationships:
            contact = item.get("contact", {})
            owner = item.get("relationship_owner", {})

            lines.append(
                "- "
                f"Contact: {contact.get('name')} ({contact.get('title')}); "
                f"Owner: {owner.get('name')}; "
                f"Strength: {item.get('relationship_strength')}; "
                f"Interactions: {item.get('interaction_count')}; "
                f"Last interaction: {item.get('last_interaction')}; "
                f"Score: {item.get('score')}"
            )

    return "\n".join(lines) if lines else "No relevant graph relationships found."