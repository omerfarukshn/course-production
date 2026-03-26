"""
Script generator — calls Claude API with prompt caching to generate lesson scripts.
"""
import os

from anthropic import Anthropic
from anthropic.types import TextBlockParam

from config import SCRIPT_MIN_WORDS, SCRIPT_MAX_WORDS, SCRIPT_STYLE


_client = None  # lazy init


SYSTEM_PROMPT = f"""You are an {SCRIPT_STYLE} creating video lesson scripts for an online course about AI character creation and monetization.

FORMAT RULES:
- Write in inline script format — each line is EITHER narration text OR a production marker on its own line.
- Production markers (use these on their own lines between narration):
  [SCREEN RECORDING: description of what to show on screen]
  [IMAGE: description of image/diagram to display]
  [VIDEO: description of video clip to show]
  [VO] — marks the start of a voiceover-only section (no visual change)
  [PAUSE] — brief pause for emphasis or transition
- Target length: {SCRIPT_MIN_WORDS}-{SCRIPT_MAX_WORDS} words of narration (excluding markers).
- Do NOT use markdown headers, bullet points, or numbered lists — just flowing narration with markers.
- Open with a hook that captures attention. Close with a clear takeaway or next step.
- Use "you" and "your" — speak directly to the student.

EXAMPLE FORMAT (8 lines):
Welcome back. Today we're building your first consistent AI character.
[SCREEN RECORDING: Open Higgsfield homepage and navigate to Nano Banana Pro]
This is where everything starts — the DNA Triangulation method.
[IMAGE: Diagram showing three reference angles — front, side, three-quarter]
Here's what makes this approach different from everything you've tried before.
[VO]
You're going to use three reference images, each from a different angle, to lock your character's face identity.
[PAUSE]
The result? A character that looks identical every single time you generate.
[SCREEN RECORDING: Side-by-side comparison of consistent outputs from the same character]

CONTENT PRIORITY RULES:
- The LESSON OUTLINE is your PRIMARY source — follow its topic, key points, and structure exactly.
- The BOOTCAMP CONTEXT is REFERENCE ONLY — extract tone, examples, and insights that reinforce the lesson outline. Never follow bootcamp tool names or workflows if they conflict with the lesson outline.
- The script title must match the lesson title, not bootcamp section headings.

Write the complete lesson script now. Remember: {SCRIPT_MIN_WORDS}-{SCRIPT_MAX_WORDS} words, inline format, production markers between narration lines."""


def _get_client() -> Anthropic:
    """Lazily initialize the Anthropic client. Raises ValueError if API key missing."""
    global _client
    if _client is None:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Add it to your .env file or set the environment variable."
            )
        _client = Anthropic(api_key=key)
    return _client


def generate_script(
    lesson_outline: str,
    bootcamp_excerpts: str,
    revision_note: str = "",
) -> str:
    """
    Generate a lesson script using Claude API with prompt caching.

    Args:
        lesson_outline: The lesson content/outline text
        bootcamp_excerpts: Pre-assembled bootcamp transcript excerpts
        revision_note: Optional note to guide revision (appended to lesson outline)

    Returns:
        Generated script text

    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set
    """
    c = _get_client()

    user_content = [
        {
            "type": "text",
            "text": f"BOOTCAMP CONTEXT (reference only):\n{bootcamp_excerpts}",
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": f"LESSON OUTLINE (primary source — write this script):\n{lesson_outline}"
            + (f"\n\nRevision note: {revision_note}" if revision_note else ""),
        },
    ]

    response = c.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        system=[
            TextBlockParam(
                type="text",
                text=SYSTEM_PROMPT,
                cache_control={"type": "ephemeral"},
            )
        ],
        messages=[{"role": "user", "content": user_content}],
    )

    u = response.usage
    print(
        f"  [cache] created={u.cache_creation_input_tokens} "
        f"read={u.cache_read_input_tokens} "
        f"in={u.input_tokens} out={u.output_tokens}"
    )

    return response.content[0].text
