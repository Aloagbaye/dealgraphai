from __future__ import annotations

from anthropic import Anthropic

from app.core.config import get_settings
from app.llm.base import BaseLLMClient, LLMResponse


class AnthropicLLMClient(BaseLLMClient):
    provider_name = "anthropic"

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic.")

        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model_name = settings.anthropic_model

    def generate(self, prompt: str) -> LLMResponse:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=900,
            temperature=0.2,
            system=(
                "You are DealGraph AI, a careful relationship-intelligence assistant. "
                "Answer only from provided context. If evidence is weak, say so."
            ),
            messages=[{"role": "user", "content": prompt}],
        )

        text_parts: list[str] = []
        for block in response.content:
            if getattr(block, "type", None) == "text":
                text_parts.append(block.text)

        return LLMResponse(
            text="\n".join(text_parts).strip(),
            provider=self.provider_name,
            model=self.model_name,
            raw=response.model_dump(),
        )
