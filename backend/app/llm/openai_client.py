from __future__ import annotations

from openai import OpenAI

from app.core.config import get_settings
from app.llm.base import BaseLLMClient, LLMResponse


class OpenAILLMClient(BaseLLMClient):
    provider_name = "openai"

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.openai_model

    def generate(self, prompt: str) -> LLMResponse:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are DealGraph AI, a careful relationship-intelligence "
                        "assistant. Answer only from provided context."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        text = response.choices[0].message.content or ""

        return LLMResponse(
            text=text,
            provider=self.provider_name,
            model=self.model_name,
            raw=response.model_dump(),
        )
