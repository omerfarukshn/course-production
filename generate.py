"""
generate.py — Main entrypoint for the script generation workflow.

Usage:
    python generate.py                     # Interactive script generation
    python generate.py --audio LESSON_ID   # Generate audio for existing script (e.g. M0L1)

Flow: module selector -> lesson selector -> context assembly -> script generation -> review loop
"""
import argparse

from rich.console import Console

from src.review_ui import show_module_menu, show_lesson_menu, review_script
from src.context_builder import assemble_context
from src.script_generator import generate_script
from src.audio_entrypoint import run_audio_generation

console = Console()


def main():
    parser = argparse.ArgumentParser(description="SahinLabs Course Production")
    parser.add_argument('--audio', metavar='LESSON_ID',
                        help='Generate audio for lesson with existing script (e.g. M0L1)')
    args, _ = parser.parse_known_args()

    if args.audio:
        run_audio_generation(args.audio)
        return

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
