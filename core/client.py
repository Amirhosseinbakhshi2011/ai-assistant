"""OpenAI-compatible chat client with streaming support."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from openai import OpenAI

from config.settings import Settings


class ChatClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
        )

    def stream_chat(
        self,
        messages: list[dict[str, str]],
    ) -> Generator[str, None, None]:
        """Yield response tokens as they arrive."""
        stream = self._client.chat.completions.create(
            model=self.settings.model,
            messages=messages,  # type: ignore[arg-type]
            temperature=self.settings.temperature,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Non-streaming convenience method."""
        return "".join(self.stream_chat(messages))
