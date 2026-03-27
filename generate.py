"""
generate.py — Main entrypoint for the script generation workflow.

Usage:
    python generate.py                     # Interactive script generation
    python generate.py --audio LESSON_ID   # Generate audio for existing script (e.g. M0L1)
    python generate.py --list              # Show lesson status table and exit

Flow: module selector -> lesson selector -> context assembly -> script generation -> review loop
"""
import argparse
import sys

# Ensure UTF-8 output on Windows (needed for emoji in status table)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from rich.console import Console
from rich.table import Table
from rich.text import Text

from src.lesson_tracker import get_all
from src.review_ui import show_module_menu, show_lesson_menu, review_script
from src.context_builder import assemble_context
from src.script_generator import generate_script
from src.audio_entrypoint import run_audio_generation

console = Console()

STATUS_EMOJI = {
    "pending": "❌",
    "scripted": "📝",
    "audio_done": "✅",
}


def show_status_table() -> None:
    """Print all lessons grouped by module with color-coded status."""
    all_lessons = get_all()

    # Group by module number (M0, M1, ... M5)
    modules: dict[str, list] = {}
    for lesson_id, info in all_lessons.items():
        module_key = lesson_id[0:2]  # "M0", "M1", etc.
        modules.setdefault(module_key, []).append((lesson_id, info))

    console.print()
    console.print("[bold cyan]  SahinLabs Course Production[/bold cyan]")
    console.print()

    for module_key in sorted(modules.keys()):
        lessons = sorted(modules[module_key], key=lambda x: x[0])
        # Print module header (bold)
        console.print(f"  [bold]MODULE {module_key[1]}[/bold]")
        for lesson_id, info in lessons:
            status = info.get("status", "pending")
            emoji = STATUS_EMOJI.get(status, "❌")
            title = info.get("title", "")
            if status == "audio_done":
                style = "green"
            elif status == "scripted":
                style = "yellow"
            else:
                style = "dim"
            console.print(f"  {emoji}  [{style}]{lesson_id:<6}[/{style}]  {title}")
        console.print()

    # Summary line
    counts = {"pending": 0, "scripted": 0, "audio_done": 0}
    for info in all_lessons.values():
        s = info.get("status", "pending")
        counts[s] = counts.get(s, 0) + 1

    console.print(
        f"  [dim]📊 Status: {counts['audio_done']} audio_done · "
        f"{counts['scripted']} scripted · {counts['pending']} pending[/dim]"
    )
    console.print()


def main():
    parser = argparse.ArgumentParser(description="SahinLabs Course Production")
    parser.add_argument('--audio', metavar='LESSON_ID',
                        help='Generate audio for lesson with existing script (e.g. M0L1)')
    parser.add_argument('--list', action='store_true',
                        help='Show lesson status table and exit')
    args, _ = parser.parse_known_args()

    if args.audio:
        run_audio_generation(args.audio)
        return

    if args.list:
        show_status_table()
        return

    show_status_table()
    console.print("  [dim]Press Enter to continue to lesson selector...[/dim]")
    input()

    while True:
        module = show_module_menu()
        if module is None:
            console.print("Goodbye!")
            break

        while True:
            lesson = show_lesson_menu(module)
            if lesson is None:
                break  # back to module selector

            try:
                console.print(
                    f"Generating script for {lesson['id']}: {lesson['title']}..."
                )
                ctx = assemble_context(module["num"], lesson["lesson_num"])
                script = generate_script(ctx["lesson_outline"], ctx["bootcamp_excerpts"])
                accepted = review_script(
                    ctx["lesson_id"],
                    ctx["lesson_title"],
                    script,
                    bootcamp_excerpts=ctx["bootcamp_excerpts"],
                    lesson_outline=ctx["lesson_outline"],
                )
                if accepted:
                    break  # back to module selector per D-15
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
            except KeyboardInterrupt:
                console.print("\nGoodbye!")
                return
            except Exception as e:
                console.print(f"[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    main()
