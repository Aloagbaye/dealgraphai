from __future__ import annotations

import re

from app.llm.base import BaseLLMClient, LLMResponse


class MockLLMClient(BaseLLMClient):
    """
    Deterministic fake LLM client for local testing.

    This allows API, frontend, retrieval, prompt, and citation workflows to be
    tested without external API keys.
    """

    provider_name = "mock"
    model_name = "deterministic-mock-llm"

    def generate(self, prompt: str) -> LLMResponse:
        source_count = len(re.findall(r"\[Source \d+\]", prompt))

        question_match = re.search(
            r"User question:\n(?P<question>.*?)\n\nRetrieved context:",
            prompt,
            flags=re.DOTALL,
        )
        question = question_match.group("question").strip() if question_match else "the user question"

        first_snippet_match = re.search(
            r"snippet:\n(?P<snippet>.*?)(?:\n\n---|\Z)",
            prompt,
            flags=re.DOTALL,
        )
        first_snippet = (
            first_snippet_match.group("snippet").strip()
            if first_snippet_match
            else "No snippet was available."
        )

        text = f"""
Answer:
Based on the retrieved CRM evidence, the best available answer to "{question}" is grounded in {source_count} retrieved source(s). The strongest evidence says: {first_snippet}

Evidence Used:
- Used the retrieved source snippets and metadata provided in the prompt.
- No facts outside the retrieved context were added.

Recommended Next Action:
- Review the cited CRM records and confirm the latest deal/contact status before taking action.

Confidence:
Medium
""".strip()

        return LLMResponse(
            text=text,
            provider=self.provider_name,
            model=self.model_name,
            raw={"source_count": source_count},
        )
