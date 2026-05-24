from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    """Standard response object returned by all LLM providers."""

    text: str
    provider: str
    model: str
    raw: dict | None = None


class BaseLLMClient(ABC):
    provider_name: str
    model_name: str

    @abstractmethod
    def generate(self, prompt: str) -> LLMResponse:
        """Generate a response from a prompt."""
        raise NotImplementedError
