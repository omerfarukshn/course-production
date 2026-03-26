"""
Review UI — interactive script review loop.
Displays generated script and handles (a)ccept / (e)dit / (r)egenerate / (s)kip actions.
Full implementation in Phase 3 Plan 02.
"""
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.panel import Panel

from src.context_builder import save_script

console = Console()


def review_script(lesson_id: str, lesson_title: str, script_text: str) -> str | None:
    """
    Display generated script and prompt for (a)ccept / (e)dit / (r)egenerate / (s)kip.

    Returns:
        "accepted" if saved, "skipped" if skipped, "regenerate" if regeneration requested
    """
    syntax = Syntax(script_text, "markdown", theme="monokai", word_wrap=True)
    console.print(Panel(syntax, title=lesson_title, border_style="cyan"))

    choice = Prompt.ask(
        "[bold]Action[/bold]: (a)ccept / (e)dit / (r)egenerate / (s)kip",
        choices=["a", "e", "r", "s"],
        default="s",
    )

    if choice == "a":
        path = save_script(lesson_id, lesson_title, script_text)
        console.print(f"[green]Saved:[/green] {path}")
        return "accepted"
    elif choice == "s":
        console.print("[yellow]Skipped.[/yellow]")
        return "skipped"
    elif choice == "r":
        return "regenerate"
    elif choice == "e":
        return "edit"

    return "skipped"
