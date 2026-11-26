"""Persist and load chat history as JSON."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ChatHistory:
    def __init__(self, data_dir: Path, session_id: str | None = None) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if session_id:
            self.session_id = session_id
        else:
            self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        self.path = self.data_dir / f"{self.session_id}.json"
        self.messages: list[dict[str, str]] = []

        if self.path.exists():
            self._load()

    def _load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.messages = data.get("messages", [])
        except (json.JSONDecodeError, OSError):
            self.messages = []

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def clear(self) -> None:
        self.messages.clear()
        self.save()

    def save(self) -> None:
        payload: dict[str, Any] = {
            "session_id": self.session_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "messages": self.messages,
        }
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def recent(self, n: int = 10) -> list[dict[str, str]]:
        return self.messages[-n:]
