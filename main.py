#!/usr/bin/env python3
"""AI Assistant — interactive terminal chat."""

from __future__ import annotations

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from config.settings import get_settings
from core.assistant import Assistant

console = Console()


def print_banner(model: str, base_url: str) -> None:
    console.print(
        Panel.fit(
            "[bold blue]AI Assistant[/bold blue]\n"
            f"[dim]Model:[/dim] {model}\n"
            f"[dim]Endpoint:[/dim] {base_url}\n\n"
            "[dim]/clear  /history  /save  /quit[/dim]",
            border_style="blue",
        )
    )


def main() -> int:
    try:
        settings = get_settings()
    except ValueError as e:
        console.print(f"[red]Config error:[/red] {e}")
        return 1

    assistant = Assistant(settings)
    print_banner(settings.model, settings.base_url)

    while True:
        try:
            user_input = console.input("\n[bold green]You ›[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Bye.[/dim]")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("/quit", "/exit", "/q"):
            console.print("[dim]Bye.[/dim]")
            break

        if cmd == "/clear":
            assistant.clear()
            console.print("[yellow]Conversation cleared.[/yellow]")
            continue

        if cmd == "/save":
            assistant.history.save()
            console.print(f"[green]Saved → {assistant.history.path}[/green]")
            continue

        if cmd == "/history":
            recent = assistant.history.recent(8)
            if not recent:
                console.print("[dim]No messages yet.[/dim]")
            else:
                for m in recent:
                    role = m["role"]
                    color = {"user": "green", "assistant": "cyan", "system": "dim"}.get(
                        role, "white"
                    )
                    preview = m["content"][:120].replace("\n", " ")
                    console.print(f"[{color}]{role}[/{color}]: {preview}")
            continue

        # Normal chat
        console.print()
        console.print("[bold cyan]Assistant ›[/bold cyan] ", end="")

        try:
            chunks: list[str] = []
            for token in assistant.reply_stream(user_input):
                console.print(token, end="")
                chunks.append(token)
            console.print()  # newline after stream

            # Optional: pretty markdown render of full reply
            full = "".join(chunks).strip()
            if full and ("```" in full or full.startswith("#") or "**" in full):
                console.print()
                console.print(Markdown(full))

        except Exception as e:
            console.print(f"\n[red]Error:[/red] {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
