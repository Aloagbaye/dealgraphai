from app.services.graph_service import get_graph_service


def main() -> None:
    print("Running graph smoke test...")

    graph = get_graph_service()
    summary = graph.graph_summary()

    assert summary["node_count"] > 0
    assert summary["edge_count"] > 0

    print("Graph summary:")
    print(summary)

    companies = graph.search_nodes(query="", node_type="company", limit=1)

    if not companies:
        print("No company found for strongest relationship test.")
        return

    company_id = companies[0]["node_id"]
    relationships = graph.strongest_relationships_for_company(company_id=company_id)

    print()
    print(f"Strongest relationships for company {company_id}:")
    for item in relationships[:5]:
        print(item)

    print()
    print("✅ Graph smoke test passed.")


if __name__ == "__main__":
    main()