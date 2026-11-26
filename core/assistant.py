"""High-level conversation manager."""

from __future__ import annotations

from collections.abc import Generator

from config.settings import Settings
from core.client import ChatClient
from core.history import ChatHistory


class Assistant:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = ChatClient(settings)
        self.history = ChatHistory(settings.data_dir)

        # Ensure system prompt is present
        if not self.history.messages or self.history.messages[0].get("role") != "system":
            self.history.messages.insert(
                0, {"role": "system", "content": settings.system_prompt}
            )

    def _build_messages(self) -> list[dict[str, str]]:
        """Return system + last N user/assistant turns."""
        system = self.history.messages[0:1]
        rest = [m for m in self.history.messages[1:] if m["role"] in ("user", "assistant")]
        max_turns = self.settings.max_history * 2
        return system + rest[-max_turns:]

    def reply_stream(self, user_text: str) -> Generator[str, None, None]:
        self.history.add("user", user_text)
        messages = self._build_messages()

        full: list[str] = []
        try:
            for token in self.client.stream_chat(messages):
                full.append(token)
                yield token
        except Exception as e:
            # Roll back the user message on hard failure
            if self.history.messages and self.history.messages[-1]["role"] == "user":
                self.history.messages.pop()
            raise e

        assistant_text = "".join(full).strip()
        if assistant_text:
            self.history.add("assistant", assistant_text)
            self.history.save()

    def clear(self) -> None:
        self.history.clear()
        self.history.add("system", self.settings.system_prompt)
        self.history.save()
