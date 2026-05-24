from __future__ import annotations

from app.core.config import get_settings
from app.llm.anthropic_client import AnthropicLLMClient
from app.llm.base import BaseLLMClient
from app.llm.mock_client import MockLLMClient
from app.llm.openai_client import OpenAILLMClient


def get_llm_client(provider: str | None = None) -> BaseLLMClient:
    settings = get_settings()
    selected_provider = (provider or settings.llm_provider).lower().strip()

    if selected_provider == "mock":
        return MockLLMClient()

    if selected_provider == "openai":
        return OpenAILLMClient()

    if selected_provider == "anthropic":
        return AnthropicLLMClient()

    raise ValueError(
        f"Unsupported LLM provider: {selected_provider}. "
        "Supported providers are: mock, openai, anthropic."
    )
