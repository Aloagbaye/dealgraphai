from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

from app.services.data_loader import (
    load_companies,
    load_contacts,
    load_deals,
    load_interactions,
    load_relationship_edges,
)


TEAM_MEMBER_NAMES = {
    "usr_001": "Priya Mehta",
    "usr_002": "James Okafor",
    "usr_003": "Sarah Chen",
    "usr_004": "Marcus Webb",
    "usr_005": "Leila Nazari",
}


@dataclass
class GraphNode:
    node_id: str
    node_type: str
    name: str
    metadata: dict[str, Any]


@dataclass
class GraphEdge:
    from_id: str
    to_id: str
    relationship_type: str
    strength_score: float
    interaction_count: int
    last_interaction: str | None
    metadata: dict[str, Any]


def _strength_to_score(value: str | float | int | None) -> float:
    if isinstance(value, int | float):
        return float(value)

    if not value:
        return 0.25

    mapping = {
        "weak": 0.25,
        "moderate": 0.50,
        "strong": 0.75,
        "champion": 0.95,
    }

    return mapping.get(str(value).lower(), 0.25)


def _contact_name(contact: dict[str, Any]) -> str:
    first_name = contact.get("first_name", "")
    last_name = contact.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip()

    if full_name:
        return full_name

    return contact.get("name", contact.get("contact_id", "Unknown Contact"))


class RelationshipGraphService:
    """
    In-memory relationship graph service.

    This service builds a graph from the synthetic CRM dataset and supports
    relationship lookup, strongest connection ranking, and warm intro paths.
    """

    def __init__(self) -> None:
        self.companies = load_companies()
        self.contacts = load_contacts()
        self.deals = load_deals()
        self.interactions = load_interactions()
        self.relationship_edges = load_relationship_edges()

        self.nodes: dict[str, GraphNode] = {}
        self.adjacency: dict[str, list[GraphEdge]] = defaultdict(list)

        self.contacts_by_id = {
            contact["contact_id"]: contact for contact in self.contacts
        }
        self.companies_by_id = {
            company["company_id"]: company for company in self.companies
        }
        self.deals_by_id = {
            deal["deal_id"]: deal for deal in self.deals
        }

        self._build_graph()

    def _add_node(
        self,
        node_id: str,
        node_type: str,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.nodes[node_id] = GraphNode(
            node_id=node_id,
            node_type=node_type,
            name=name,
            metadata=metadata or {},
        )

    def _add_edge(
        self,
        from_id: str,
        to_id: str,
        relationship_type: str,
        strength_score: float = 0.5,
        interaction_count: int = 0,
        last_interaction: str | None = None,
        metadata: dict[str, Any] | None = None,
        bidirectional: bool = True,
    ) -> None:
        edge = GraphEdge(
            from_id=from_id,
            to_id=to_id,
            relationship_type=relationship_type,
            strength_score=strength_score,
            interaction_count=interaction_count,
            last_interaction=last_interaction,
            metadata=metadata or {},
        )

        self.adjacency[from_id].append(edge)

        if bidirectional:
            reverse_edge = GraphEdge(
                from_id=to_id,
                to_id=from_id,
                relationship_type=relationship_type,
                strength_score=strength_score,
                interaction_count=interaction_count,
                last_interaction=last_interaction,
                metadata=metadata or {},
            )
            self.adjacency[to_id].append(reverse_edge)

    def _build_graph(self) -> None:
        # Team member nodes
        for user_id, name in TEAM_MEMBER_NAMES.items():
            self._add_node(
                node_id=user_id,
                node_type="team_member",
                name=name,
                metadata={"email": f"{name.lower().replace(' ', '.')}@vc-firm.com"},
            )

        # Company nodes
        for company in self.companies:
            self._add_node(
                node_id=company["company_id"],
                node_type="company",
                name=company.get("name", company["company_id"]),
                metadata=company,
            )

        # Contact nodes + contact-company edges + owner-contact edges
        for contact in self.contacts:
            contact_id = contact["contact_id"]
            company_id = contact.get("company_id")
            owner_id = contact.get("relationship_owner")

            self._add_node(
                node_id=contact_id,
                node_type="contact",
                name=_contact_name(contact),
                metadata=contact,
            )

            if company_id:
                self._add_edge(
                    from_id=contact_id,
                    to_id=company_id,
                    relationship_type="works_at",
                    strength_score=0.8,
                    interaction_count=int(contact.get("interaction_count", 0)),
                    last_interaction=contact.get("last_interaction"),
                    metadata={"source": "contact_company"},
                )

            if owner_id:
                self._add_edge(
                    from_id=owner_id,
                    to_id=contact_id,
                    relationship_type="owns_relationship",
                    strength_score=_strength_to_score(contact.get("relationship_strength")),
                    interaction_count=int(contact.get("interaction_count", 0)),
                    last_interaction=contact.get("last_interaction"),
                    metadata={"source": "relationship_owner"},
                )

        # Deal nodes + deal-company + deal-team edges
        for deal in self.deals:
            deal_id = deal["deal_id"]
            company_id = deal.get("company_id")

            self._add_node(
                node_id=deal_id,
                node_type="deal",
                name=deal.get("name", deal_id),
                metadata=deal,
            )

            if company_id:
                self._add_edge(
                    from_id=deal_id,
                    to_id=company_id,
                    relationship_type="deal_for_company",
                    strength_score=0.7,
                    interaction_count=0,
                    last_interaction=deal.get("updated_at"),
                    metadata={"source": "deal_company"},
                )

            for user_id in deal.get("deal_team", []):
                self._add_edge(
                    from_id=user_id,
                    to_id=deal_id,
                    relationship_type="works_on_deal",
                    strength_score=0.7,
                    interaction_count=0,
                    last_interaction=deal.get("updated_at"),
                    metadata={"source": "deal_team"},
                )

        # Explicit relationship edges if present
        for edge in self.relationship_edges:
            from_id = edge.get("from_id") or edge.get("person_a")
            to_id = edge.get("to_id") or edge.get("person_b")

            if not from_id or not to_id:
                continue

            self._add_edge(
                from_id=from_id,
                to_id=to_id,
                relationship_type=edge.get("relationship_type", "relationship"),
                strength_score=float(edge.get("strength_score", edge.get("strength", 0.5))),
                interaction_count=int(edge.get("interaction_count", 0)),
                last_interaction=edge.get("last_interaction"),
                metadata=edge,
            )

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        node = self.nodes.get(node_id)

        if not node:
            return None

        return {
            "node_id": node.node_id,
            "node_type": node.node_type,
            "name": node.name,
            "metadata": node.metadata,
        }

    def search_nodes(self, query: str, node_type: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        query_lower = query.lower()
        matches = []

        for node in self.nodes.values():
            if node_type and node.node_type != node_type:
                continue

            name_match = query_lower in node.name.lower()
            metadata_match = query_lower in str(node.metadata).lower()

            if name_match or metadata_match:
                matches.append(
                    {
                        "node_id": node.node_id,
                        "node_type": node.node_type,
                        "name": node.name,
                        "metadata": node.metadata,
                        "match_reason": "name" if name_match else "metadata",
                    }
                )

        return matches[:limit]

    def get_neighbors(self, node_id: str, limit: int = 20) -> list[dict[str, Any]]:
        neighbors = []

        for edge in self.adjacency.get(node_id, []):
            node = self.nodes.get(edge.to_id)

            if not node:
                continue

            neighbors.append(
                {
                    "node": {
                        "node_id": node.node_id,
                        "node_type": node.node_type,
                        "name": node.name,
                    },
                    "edge": {
                        "relationship_type": edge.relationship_type,
                        "strength_score": edge.strength_score,
                        "interaction_count": edge.interaction_count,
                        "last_interaction": edge.last_interaction,
                        "metadata": edge.metadata,
                    },
                }
            )

        neighbors.sort(
            key=lambda item: (
                item["edge"]["strength_score"],
                item["edge"]["interaction_count"],
            ),
            reverse=True,
        )

        return neighbors[:limit]

    def strongest_relationships_for_company(
        self,
        company_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        company_contacts = [
            contact
            for contact in self.contacts
            if contact.get("company_id") == company_id
        ]

        ranked = []

        for contact in company_contacts:
            contact_id = contact["contact_id"]
            owner_id = contact.get("relationship_owner")
            owner_name = TEAM_MEMBER_NAMES.get(owner_id, owner_id)

            ranked.append(
                {
                    "contact": {
                        "contact_id": contact_id,
                        "name": _contact_name(contact),
                        "title": contact.get("title"),
                        "relationship_strength": contact.get("relationship_strength"),
                        "interaction_count": contact.get("interaction_count"),
                        "last_interaction": contact.get("last_interaction"),
                    },
                    "relationship_owner": {
                        "user_id": owner_id,
                        "name": owner_name,
                    },
                    "score": round(
                        _strength_to_score(contact.get("relationship_strength"))
                        + min(int(contact.get("interaction_count", 0)) / 100, 0.4),
                        4,
                    ),
                }
            )

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:limit]

    def strongest_relationships_for_contact(
        self,
        contact_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        contact = self.contacts_by_id.get(contact_id)

        if not contact:
            return []

        owner_id = contact.get("relationship_owner")
        owner_name = TEAM_MEMBER_NAMES.get(owner_id, owner_id)

        relationships = [
            {
                "relationship_owner": {
                    "user_id": owner_id,
                    "name": owner_name,
                },
                "contact": {
                    "contact_id": contact_id,
                    "name": _contact_name(contact),
                    "title": contact.get("title"),
                    "company_id": contact.get("company_id"),
                },
                "relationship_strength": contact.get("relationship_strength"),
                "interaction_count": contact.get("interaction_count"),
                "last_interaction": contact.get("last_interaction"),
                "score": round(
                    _strength_to_score(contact.get("relationship_strength"))
                    + min(int(contact.get("interaction_count", 0)) / 100, 0.4),
                    4,
                ),
            }
        ]

        return relationships[:limit]

    def find_paths(
        self,
        start_id: str,
        target_id: str,
        max_depth: int = 4,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Breadth-first path search.

        Finds short relationship paths between two nodes.
        """

        if start_id not in self.nodes or target_id not in self.nodes:
            return []

        queue = deque()
        queue.append((start_id, [start_id], []))

        paths = []
        visited_paths = set()

        while queue and len(paths) < limit:
            current_id, path_nodes, path_edges = queue.popleft()

            if len(path_nodes) > max_depth + 1:
                continue

            if current_id == target_id:
                path_key = tuple(path_nodes)

                if path_key not in visited_paths:
                    paths.append(
                        self._format_path(path_nodes, path_edges)
                    )
                    visited_paths.add(path_key)

                continue

            for edge in self.adjacency.get(current_id, []):
                next_id = edge.to_id

                if next_id in path_nodes:
                    continue

                queue.append(
                    (
                        next_id,
                        path_nodes + [next_id],
                        path_edges + [edge],
                    )
                )

        paths.sort(key=lambda item: item["path_score"], reverse=True)
        return paths[:limit]

    def _format_path(
        self,
        path_nodes: list[str],
        path_edges: list[GraphEdge],
    ) -> dict[str, Any]:
        formatted_nodes = []

        for node_id in path_nodes:
            node = self.nodes[node_id]
            formatted_nodes.append(
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type,
                    "name": node.name,
                }
            )

        formatted_edges = []

        for edge in path_edges:
            formatted_edges.append(
                {
                    "from_id": edge.from_id,
                    "to_id": edge.to_id,
                    "relationship_type": edge.relationship_type,
                    "strength_score": edge.strength_score,
                    "interaction_count": edge.interaction_count,
                    "last_interaction": edge.last_interaction,
                }
            )

        if path_edges:
            avg_strength = sum(edge.strength_score for edge in path_edges) / len(path_edges)
            total_interactions = sum(edge.interaction_count for edge in path_edges)
            path_score = avg_strength + min(total_interactions / 100, 0.5)
        else:
            path_score = 0.0

        return {
            "nodes": formatted_nodes,
            "edges": formatted_edges,
            "path_length": max(len(path_nodes) - 1, 0),
            "path_score": round(path_score, 4),
        }

    def find_warm_intro_paths(
        self,
        target_contact_id: str,
        starting_team_member_id: str | None = None,
        max_depth: int = 4,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Finds possible intro paths from team members to a target contact.

        If starting_team_member_id is provided, search from that team member.
        Otherwise, search from all known team members.
        """

        starts = [starting_team_member_id] if starting_team_member_id else list(TEAM_MEMBER_NAMES.keys())

        candidate_paths = []

        for start_id in starts:
            paths = self.find_paths(
                start_id=start_id,
                target_id=target_contact_id,
                max_depth=max_depth,
                limit=limit,
            )
            candidate_paths.extend(paths)

        candidate_paths.sort(key=lambda item: item["path_score"], reverse=True)
        return candidate_paths[:limit]

    def graph_summary(self) -> dict[str, Any]:
        node_type_counts: dict[str, int] = defaultdict(int)
        edge_type_counts: dict[str, int] = defaultdict(int)

        for node in self.nodes.values():
            node_type_counts[node.node_type] += 1

        for edges in self.adjacency.values():
            for edge in edges:
                edge_type_counts[edge.relationship_type] += 1

        return {
            "node_count": len(self.nodes),
            "edge_count": sum(len(edges) for edges in self.adjacency.values()),
            "node_type_counts": dict(node_type_counts),
            "edge_type_counts": dict(edge_type_counts),
        }


_graph_service: RelationshipGraphService | None = None


def get_graph_service() -> RelationshipGraphService:
    global _graph_service

    if _graph_service is None:
        _graph_service = RelationshipGraphService()

    return _graph_service


def reset_graph_service() -> None:
    global _graph_service
    _graph_service = None