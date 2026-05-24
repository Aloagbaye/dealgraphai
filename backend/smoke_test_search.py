from app.services.search_service import search_documents


def main() -> None:
    print("Running search smoke test...")

    response = search_documents(
        query="fundraising timeline",
        limit=5,
    )

    assert response["query"] == "fundraising timeline"
    assert response["total_candidates"] > 0
    assert "results" in response

    print(f"Total candidates: {response['total_candidates']}")
    print(f"Total matches: {response['total_matches']}")

    for index, result in enumerate(response["results"], start=1):
        print()
        print(f"Result {index}")
        print(f"  doc_id: {result['doc_id']}")
        print(f"  title: {result['title']}")
        print(f"  score: {result['score']}")
        print(f"  matched_terms: {result['matched_terms']}")
        print(f"  snippet: {result['snippet'][:180]}")

    print()
    print("✅ Search smoke test passed.")


if __name__ == "__main__":
    main()