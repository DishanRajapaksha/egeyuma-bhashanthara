from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class ModelClientError(Exception):
    """Raised when a model request fails or returns unusable output."""


@dataclass(frozen=True)
class ModelResponse:
    content: str
    model: str


@dataclass(frozen=True)
class OpenAICompatibleClient:
    model: str
    base_url: str
    api_key: str = "local-key"
    temperature: float = 0.0
    max_tokens: int = 2048
    timeout_seconds: float = 120.0

    def complete(self, prompt: str) -> ModelResponse:
        url = self.base_url.rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # pragma: no cover - provider-specific exceptions vary.
            raise ModelClientError(f"Model request failed for {self.model}: {exc}") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelClientError(
                f"Unexpected model response shape for {self.model}: {data}"
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise ModelClientError(f"Empty model response for {self.model}")

        return ModelResponse(content=content.strip(), model=self.model)
