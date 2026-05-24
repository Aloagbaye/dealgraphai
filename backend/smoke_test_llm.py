from app.llm.factory import get_llm_client


def main() -> None:
    print("Running LLM smoke test...")

    client = get_llm_client("mock")
    response = client.generate(
        """
User question:
What did the team discuss?

Retrieved context:
[Source 1]
snippet:
The team discussed fundraising timeline and customer traction.
"""
    )

    assert response.text
    assert response.provider == "mock"

    print(f"Provider: {response.provider}")
    print(f"Model: {response.model}")
    print()
    print(response.text)
    print()
    print("✅ LLM smoke test passed.")


if __name__ == "__main__":
    main()
