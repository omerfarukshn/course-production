"""
Narration extractor — parse script .md files into clean TTS narration text.
Strips headings (#), standalone markers ([PAUSE], [VO], [SCREEN RECORDING:...], etc.)
Keeps all other non-empty lines joined with spaces.
"""
import re
from pathlib import Path
from config import SCRIPTS_DIR


def extract_narration(script_path: Path) -> str:
    """Extract plain narration text from a script .md file.

    Strips: headings (#), standalone markers (lines matching ^\\[.+\\]$)
    Keeps: all other non-empty lines joined with spaces.

    Returns empty string for empty/marker-only scripts.
    """
    content = script_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    narration = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            continue
        if re.match(r'^\[.+\]$', stripped):
            continue
        narration.append(stripped)
    return ' '.join(narration)


def find_script_path(lesson_id: str) -> Path | None:
    """Find script file for a lesson ID like 'M0L1'.

    Globs SCRIPTS_DIR for {lesson_id}_*.md and returns first match.
    Returns None if no matching script found.
    """
    matches = list(SCRIPTS_DIR.glob(f"{lesson_id}_*.md"))
    return matches[0] if matches else None
