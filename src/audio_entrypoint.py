"""
Audio entrypoint — orchestrates narration extraction, TTS generation, quality check, and status update.

Usage: called by generate.py when --audio LESSON_ID is passed.
"""
import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

from src.narration_extractor import find_script_path, extract_narration
from src.audio_generator import generate_audio
from src.lesson_tracker import get_status, set_status

console = Console()


def run_audio_generation(lesson_id: str) -> None:
    """Full audio generation flow for a single lesson.

    Steps:
    1. Validate lesson has a script (status == 'scripted')
    2. Find script file via glob
    3. Extract narration text
    4. Generate WAV via Kokoro
    5. Print quality stats (duration, size, path, word-count ratio)
    6. Prompt (p)lay / (s)kip
    7. Update status to 'audio_done'
    """
    # Step 1: Status guard
    status = get_status(lesson_id)
    if status == "audio_done":
        console.print(f"[yellow]{lesson_id} already has audio (status: audio_done). Skipping.[/yellow]")
        return
    if status != "scripted":
        console.print(f"[red]Error: {lesson_id} has no approved script (status: {status}).[/red]")
        console.print("Run [bold]python generate.py[/bold] first to generate and approve a script.")
        return

    # Step 2: Find script
    script_path = find_script_path(lesson_id)
    if script_path is None:
        console.print(f"[red]Error: No script file found for {lesson_id} in scripts/ directory.[/red]")
        return

    console.print(f"Found script: [cyan]{script_path.name}[/cyan]")

    # Step 3: Extract narration
    narration = extract_narration(script_path)
    if not narration.strip():
        console.print(f"[red]Error: Script {script_path.name} has no narration text after extraction.[/red]")
        return

    word_count = len(narration.split())
    console.print(f"Narration: {word_count} words, {len(narration)} chars")

    # Step 4: Generate audio
    # Extract slug from script filename: M0L1_welcome_something.md -> welcome_something
    slug = script_path.stem.split("_", 1)[1] if "_" in script_path.stem else "audio"

    console.print(f"[bold]Generating audio with Kokoro TTS...[/bold]")
    result = generate_audio(lesson_id, narration, slug)

    # Step 5: Quality stats
    duration = result["duration"]
    output_path = result["path"]
    size_kb = output_path.stat().st_size // 1024
    expected_seconds = word_count / 2.5  # 150 words per minute
    ratio = duration / expected_seconds if expected_seconds > 0 else 0

    console.print()
    console.print(f"[green bold]Audio generated successfully![/green bold]")
    console.print(f"  Duration:  {duration:.1f}s (expected ~{expected_seconds:.0f}s, ratio {ratio:.2f})")
    console.print(f"  File size: {size_kb} KB")
    console.print(f"  Path:      {output_path}")

    if not (0.85 <= ratio <= 1.15):
        console.print("[yellow]  Warning: duration outside +/-15% of word-count estimate[/yellow]")

    # Step 6: Play/skip prompt
    choice = Prompt.ask("(p)lay / (s)kip", choices=["p", "s"], default="s")
    if choice == "p":
        try:
            if sys.platform == "win32":
                subprocess.Popen(["start", "", str(output_path)], shell=True)
            else:
                subprocess.Popen(["xdg-open", str(output_path)])
            console.print("[dim]Playing audio...[/dim]")
        except Exception as e:
            console.print(f"[yellow]Could not play audio: {e}[/yellow]")
            console.print(f"Open manually: {output_path}")

    # Step 7: Mark as audio_done
    set_status(lesson_id, "audio_done")
    console.print(f"[green]Status updated: {lesson_id} -> audio_done[/green]")
