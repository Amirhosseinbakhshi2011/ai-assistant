"""Load configuration from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Project root (parent of config/)
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    system_prompt: str
    max_history: int
    temperature: float
    data_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "API_KEY is missing. Copy .env.example to .env and set your key."
            )

        return cls(
            api_key=api_key,
            base_url=os.getenv("BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            model=os.getenv("MODEL", "gpt-4o-mini"),
            system_prompt=os.getenv(
                "SYSTEM_PROMPT",
                "You are a helpful, concise, and friendly AI assistant.",
            ),
            max_history=int(os.getenv("MAX_HISTORY", "20")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            data_dir=ROOT / "data" / "chats",
        )


def get_settings() -> Settings:
    return Settings.from_env()
