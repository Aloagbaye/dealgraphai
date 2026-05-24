from app.rag.answer_service import answer_question


def main() -> None:
    print("Running RAG smoke test with LLM provider abstraction...")

    response = answer_question(
        question="What did the team discuss about fundraising timeline?",
        limit=5,
        llm_provider="mock",
    )

    assert response["question"]
    assert response["answer"]
    assert response["llm"]["provider"] == "mock"
    assert response["retrieval_summary"]
    assert "citations" in response

    print()
    print("Question:")
    print(response["question"])

    print()
    print("LLM:")
    print(response["llm"])

    print()
    print("Answer:")
    print(response["answer"][:1000])

    print()
    print("Citations:")
    for citation in response["citations"]:
        print(
            f"- {citation.title} | {citation.source_type} | "
            f"{citation.date} | score={citation.score}"
        )

    print()
    print("✅ RAG smoke test passed.")


if __name__ == "__main__":
    main()
