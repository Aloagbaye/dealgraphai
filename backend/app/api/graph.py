from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.services.data_loader import DataFileNotFoundError
from app.services.graph_service import get_graph_service


router = APIRouter()


@router.get("/summary")
def get_graph_summary() -> dict[str, Any]:
    try:
        graph = get_graph_service()
        return graph.graph_summary()
    except DataFileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/nodes/search")
def search_graph_nodes(
    q: str = Query(..., min_length=1),
    node_type: str | None = None,
    limit: int = Query(default=10, ge=1, le=50),
) -> list[dict[str, Any]]:
    graph = get_graph_service()
    return graph.search_nodes(query=q, node_type=node_type, limit=limit)


@router.get("/nodes/{node_id}")
def get_graph_node(node_id: str) -> dict[str, Any]:
    graph = get_graph_service()
    node = graph.get_node(node_id)

    if not node:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")

    return node


@router.get("/nodes/{node_id}/neighbors")
def get_graph_neighbors(
    node_id: str,
    limit: int = Query(default=20, ge=1, le=100),
) -> list[dict[str, Any]]:
    graph = get_graph_service()

    if not graph.get_node(node_id):
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")

    return graph.get_neighbors(node_id=node_id, limit=limit)


@router.get("/companies/{company_id}/strongest-relationships")
def get_strongest_relationships_for_company(
    company_id: str,
    limit: int = Query(default=10, ge=1, le=50),
) -> list[dict[str, Any]]:
    graph = get_graph_service()

    if not graph.get_node(company_id):
        raise HTTPException(status_code=404, detail=f"Company not found: {company_id}")

    return graph.strongest_relationships_for_company(
        company_id=company_id,
        limit=limit,
    )


@router.get("/contacts/{contact_id}/strongest-relationships")
def get_strongest_relationships_for_contact(
    contact_id: str,
    limit: int = Query(default=10, ge=1, le=50),
) -> list[dict[str, Any]]:
    graph = get_graph_service()

    if not graph.get_node(contact_id):
        raise HTTPException(status_code=404, detail=f"Contact not found: {contact_id}")

    return graph.strongest_relationships_for_contact(
        contact_id=contact_id,
        limit=limit,
    )


@router.get("/paths")
def find_relationship_paths(
    start_id: str = Query(..., min_length=1),
    target_id: str = Query(..., min_length=1),
    max_depth: int = Query(default=4, ge=1, le=6),
    limit: int = Query(default=5, ge=1, le=20),
) -> list[dict[str, Any]]:
    graph = get_graph_service()

    if not graph.get_node(start_id):
        raise HTTPException(status_code=404, detail=f"Start node not found: {start_id}")

    if not graph.get_node(target_id):
        raise HTTPException(status_code=404, detail=f"Target node not found: {target_id}")

    return graph.find_paths(
        start_id=start_id,
        target_id=target_id,
        max_depth=max_depth,
        limit=limit,
    )


@router.get("/warm-intros")
def find_warm_intro_paths(
    target_contact_id: str = Query(..., min_length=1),
    starting_team_member_id: str | None = None,
    max_depth: int = Query(default=4, ge=1, le=6),
    limit: int = Query(default=5, ge=1, le=20),
) -> list[dict[str, Any]]:
    graph = get_graph_service()

    if not graph.get_node(target_contact_id):
        raise HTTPException(
            status_code=404,
            detail=f"Target contact not found: {target_contact_id}",
        )

    if starting_team_member_id and not graph.get_node(starting_team_member_id):
        raise HTTPException(
            status_code=404,
            detail=f"Starting team member not found: {starting_team_member_id}",
        )

    return graph.find_warm_intro_paths(
        target_contact_id=target_contact_id,
        starting_team_member_id=starting_team_member_id,
        max_depth=max_depth,
        limit=limit,
    )