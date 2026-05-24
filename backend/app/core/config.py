from __future__ import annotations

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    Environment variables are loaded from backend/.env when running locally.
    Keep secrets out of source control.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "DealGraph AI API"
    app_version: str = "0.4.0"

    # Supported values: mock, openai, anthropic
    llm_provider: str = Field(default="mock")

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-haiku-latest"

    # Local development guardrail for prompt/context size.
    max_context_chars: int = 8_000


@lru_cache
def get_settings() -> Settings:
    return Settings()
