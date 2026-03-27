"""
generate.py — Main entrypoint for the script generation workflow.

Usage:
    python generate.py                     # Interactive script generation
    python generate.py --audio LESSON_ID   # Generate audio for existing script (e.g. M0L1)
    python generate.py --list              # Show lesson status table and exit
    python generate.py --lesson LESSON_ID  # Run full flow for a specific lesson (e.g. M0L1)
    python generate.py --dry-run LESSON_ID # Show assembled context without calling any API

Flow: module selector -> lesson selector -> context assembly -> script generation -> review loop
"""
import argparse
import re
import sys
import time

# Ensure UTF-8 output on Windows (needed for emoji in status table)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import anthropic

from rich.console import Console
from rich.table import Table
from rich.text import Text

from src.lesson_tracker import get_all, get_status
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


def parse_lesson_id(lesson_id: str) -> tuple:
    """Parse 'M0L1' -> ('0', '1'). Raises ValueError on bad format."""
    m = re.match(r'^M(\d+)L(\d+)$', lesson_id.strip().upper())
    if not m:
        raise ValueError(
            f"Invalid lesson ID '{lesson_id}'. Expected format: M0L1, M1L3, etc."
        )
    return m.group(1), m.group(2)


def generate_script_with_retry(lesson_outline: str, bootcamp_excerpts: str) -> str:
    """Call generate_script(), retry once on API error with 10s delay."""
    try:
        return generate_script(lesson_outline, bootcamp_excerpts)
    except anthropic.APIError as e:
        console.print(f"[yellow]Claude API error. Retrying in 10s... (1/2)[/yellow]")
        console.print(f"[dim]{e}[/dim]")
        time.sleep(10)
        return generate_script(lesson_outline, bootcamp_excerpts)


def run_lesson_flow(lesson_id: str) -> None:
    """Full flow: context -> script -> review -> optional audio."""
    try:
        module_num, lesson_num = parse_lesson_id(lesson_id)
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        return

    # Override check
    status = get_status(lesson_id)
    if status in ("scripted", "audio_done"):
        from rich.prompt import Prompt
        console.print(f"[yellow]{lesson_id} is already {status}.[/yellow]")
        choice = Prompt.ask("Regenerate? (y/n)", choices=["y", "n"], default="n")
        if choice == "n":
            console.print("Exiting without changes.")
            return

    # Context assembly
    console.print(f"[bold]Assembling context for {lesson_id}...[/bold]")
    try:
        ctx = assemble_context(module_num, lesson_num)
    except FileNotFoundError:
        console.print(
            "[red]❌ Course file not found: sources/sahinlabs_course.txt. "
            "Fix: add the course content file and restart.[/red]"
        )
        return
    except Exception as e:
        console.print(f"[red]❌ Context assembly failed: {e}[/red]")
        return

    # Script generation
    console.print(f"[bold]Generating script for {ctx['lesson_title']}...[/bold]")
    try:
        script = generate_script_with_retry(ctx["lesson_outline"], ctx["bootcamp_excerpts"])
    except anthropic.APIError as e:
        import pathlib
        pathlib.Path("temp_context.txt").write_text(
            ctx["lesson_outline"] + "\n\n" + ctx["bootcamp_excerpts"], encoding="utf-8"
        )
        console.print(
            f"[red]❌ Claude API error after retry: {e}. "
            f"Context saved to temp_context.txt. "
            f"Fix: check ANTHROPIC_API_KEY in .env[/red]"
        )
        return
    except Exception as e:
        console.print(f"[red]❌ Script generation failed: {e}[/red]")
        return

    # Review loop
    accepted = review_script(
        ctx["lesson_id"],
        ctx["lesson_title"],
        script,
        bootcamp_excerpts=ctx["bootcamp_excerpts"],
        lesson_outline=ctx["lesson_outline"],
    )

    if not accepted:
        return

    # Audio generation prompt
    from rich.prompt import Prompt
    generate_audio_choice = Prompt.ask(
        "\nGenerate audio now? (y/n)", choices=["y", "n"], default="n"
    )
    if generate_audio_choice == "y":
        try:
            run_audio_generation(lesson_id)
        except RuntimeError as e:
            console.print(f"[red]❌ {e}[/red]")
        except Exception as e:
            console.print(f"[red]❌ Audio generation failed: {e}[/red]")


def run_dry_run(lesson_id: str) -> None:
    """Show assembled context + token estimate. No API calls."""
    try:
        module_num, lesson_num = parse_lesson_id(lesson_id)
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        return

    console.print(f"[bold cyan]Dry run: {lesson_id}[/bold cyan]")
    console.print("[dim]No API calls will be made.[/dim]\n")

    try:
        ctx = assemble_context(module_num, lesson_num)
    except FileNotFoundError:
        console.print(
            "[red]❌ Course file not found: sources/sahinlabs_course.txt. "
            "Fix: add the course content file and restart.[/red]"
        )
        return
    except Exception as e:
        console.print(f"[red]❌ Failed to assemble context: {e}[/red]")
        return

    console.print(f"[bold]Lesson:[/bold] {ctx['lesson_title']}")
    console.print()
    console.print("[bold]Lesson Outline:[/bold]")
    console.print(ctx["lesson_outline"])
    console.print()
    console.print("[bold]Bootcamp Excerpts (top 5):[/bold]")
    excerpts = ctx["bootcamp_excerpts"]
    console.print(excerpts[:2000] + "..." if len(excerpts) > 2000 else excerpts)
    console.print()

    # Token estimate (rough: chars / 4)
    total_chars = len(ctx["lesson_outline"]) + len(ctx["bootcamp_excerpts"])
    token_estimate = total_chars // 4
    console.print(f"[dim]Approx input tokens: ~{token_estimate:,} (estimated from char count / 4)[/dim]")


def main():
    parser = argparse.ArgumentParser(description="SahinLabs Course Production")
    parser.add_argument('--audio', metavar='LESSON_ID',
                        help='Generate audio for lesson with existing script (e.g. M0L1)')
    parser.add_argument('--list', action='store_true',
                        help='Show lesson status table and exit')
    parser.add_argument('--lesson', metavar='LESSON_ID',
                        help='Run full flow for a specific lesson (e.g. M0L1)')
    parser.add_argument('--dry-run', metavar='LESSON_ID', dest='dry_run',
                        help='Show assembled context without calling any API (e.g. M0L1)')
    args, _ = parser.parse_known_args()

    if args.audio:
        run_audio_generation(args.audio)
        return

    if args.list:
        show_status_table()
        return

    if args.dry_run:
        run_dry_run(args.dry_run)
        return

    if args.lesson:
        run_lesson_flow(args.lesson)
        return

    try:
        show_status_table()
    except FileNotFoundError:
        console.print(
            "[red]❌ Required file not found. "
            "Fix: ensure sources/sahinlabs_course.txt exists.[/red]"
        )
        return

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
