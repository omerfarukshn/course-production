"""
Review UI — interactive script review loop.
Displays generated script and handles (a)ccept / (e)dit / (r)egenerate / (s)kip actions.
"""
import os
import subprocess
import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import IntPrompt, Prompt
from rich.text import Text

from src.context_builder import (
    list_modules,
    list_lessons_for_module,
    assemble_context,
    save_script,
)
from src.script_generator import generate_script

console = Console()

STATUS_STYLES = {
    "pending": "yellow",
    "scripted": "green",
    "audio_done": "blue",
}


def show_module_menu() -> dict | None:
    """
    Display numbered module table and prompt user to select.

    Returns:
        Module dict {"num": str, "title": str} or None if user quits.
    """
    modules = list_modules()

    table = Table(title="Modules")
    table.add_column("#", style="bold")
    table.add_column("Module")

    for i, mod in enumerate(modules, start=1):
        table.add_row(str(i), mod["title"])
    table.add_row("0", "Quit")

    console.print(table)

    choices = [str(i) for i in range(len(modules) + 1)]
    choice = IntPrompt.ask("Select module", choices=choices, default=0)

    if choice == 0:
        return None
    return modules[choice - 1]


def show_lesson_menu(module: dict) -> dict | None:
    """
    Display lessons for a module with status and prompt user to select.

    Returns:
        Lesson dict or None if user selects Back.
    """
    lessons = list_lessons_for_module(module["num"])

    table = Table(title=f"Module {module['num']}: {module['title']}")
    table.add_column("#", style="bold")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Status")

    for i, les in enumerate(lessons, start=1):
        status_text = Text(les["status"], style=STATUS_STYLES.get(les["status"], "white"))
        table.add_row(str(i), les["id"], les["title"], status_text)
    table.add_row("0", "", "Back to modules", "")

    console.print(table)

    choices = [str(i) for i in range(len(lessons) + 1)]
    choice = IntPrompt.ask("Select lesson", choices=choices, default=0)

    if choice == 0:
        return None
    return lessons[choice - 1]


def display_script(script_text: str, lesson_title: str) -> None:
    """Render script in a cyan-bordered panel with word count."""
    syntax = Syntax(script_text, "markdown", theme="monokai", word_wrap=True)
    console.print(Panel(syntax, title=lesson_title, border_style="cyan"))
    wc = len(script_text.split())
    console.print(f"  Word count: {wc}")


def open_in_editor(content: str) -> str:
    """
    Open content in $EDITOR (fallback: notepad), return edited text.
    Temp file is always cleaned up.
    """
    editor = os.environ.get("EDITOR", "notepad")
    editor_parts = editor.split()
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".md", mode="w", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        subprocess.run(editor_parts + [tmp_path], check=False)
        return Path(tmp_path).read_text(encoding="utf-8")
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


def review_script(
    lesson_id: str,
    lesson_title: str,
    script_text: str,
    bootcamp_excerpts: str = "",
    lesson_outline: str = "",
) -> bool:
    """
    Display script and run the (a)ccept / (e)dit / (r)egenerate / (s)kip loop.

    Returns:
        True if script was accepted and saved, False if skipped.
    """
    display_script(script_text, lesson_title)

    while True:
        choice = Prompt.ask(
            "(a)ccept / (e)dit / (r)egenerate / (s)kip",
            choices=["a", "e", "r", "s"],
            default="s",
        )

        if choice == "a":
            path = save_script(lesson_id, lesson_title, script_text)
            console.print(f"[green]Saved:[/green] {path}")
            return True

        elif choice == "s":
            console.print("[yellow]Skipped.[/yellow]")
            return False

        elif choice == "e":
            edited = open_in_editor(script_text)
            display_script(edited, lesson_title)
            confirm = Prompt.ask(
                "(a)ccept edited / (d)iscard",
                choices=["a", "d"],
                default="d",
            )
            if confirm == "a":
                path = save_script(lesson_id, lesson_title, edited)
                console.print(f"[green]Saved:[/green] {path}")
                return True
            # discard: fall through and re-display original in next loop iteration
            display_script(script_text, lesson_title)

        elif choice == "r":
            note = Prompt.ask("Regenerate with note")
            script_text = generate_script(
                lesson_outline, bootcamp_excerpts, revision_note=note
            )
            display_script(script_text, lesson_title)
