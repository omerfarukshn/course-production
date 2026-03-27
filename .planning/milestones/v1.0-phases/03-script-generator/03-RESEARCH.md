# Phase 3: Script Generator - Research

**Researched:** 2026-03-26
**Domain:** Anthropic Python SDK (prompt caching), Rich terminal UI, subprocess editor integration
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Inline marker format (single column) — NOT two-column AV table.
- **D-02:** Each line is either narration text or a production marker on its own line.
- **D-03:** Markers: `[SCREEN RECORDING: description]`, `[IMAGE: description]`, `[VIDEO: description]`, `[VO]`, `[PAUSE]`.
- **D-04:** Target length: 300-600 words (as defined in `config.py`: `SCRIPT_MIN_WORDS=300`, `SCRIPT_MAX_WORDS=600`). Do NOT change these constants.
- **D-05:** Saved as `scripts/M{n}L{n}_{slug}.md` — Markdown file, inline format, no extra headers needed beyond lesson title.
- **D-06:** Rich interactive menu — NOT CLI argument. Run with `python generate.py`, no args needed.
- **D-07:** Module selection first (M0–M5), then lesson list within that module.
- **D-08:** Each lesson row shows: `{ID} | {Title} | {status}` — e.g., `M1L1 | Character Bible | pending`.
- **D-09:** Status colors via `rich`: pending = yellow, scripted = green, audio_done = blue.
- **D-10:** User can navigate back to module list from lesson list.
- **D-11:** `(a)ccept` — save script to `scripts/M{n}L{n}_{slug}.md`, mark status `scripted`, return to lesson selector.
- **D-12:** `(e)dit` — write script to temp `.md` file, open with `$EDITOR` (fallback: `notepad` on Windows), read back after editor closes, re-display modified script, ask accept/discard.
- **D-13:** `(r)egenerate` — prompt user for a note, append as `"\n\nRevision note: {note}"`, call API again.
- **D-14:** `(s)kip` — do nothing, return to lesson selector (status stays `pending`).
- **D-15:** After accept: immediately return to module selector. No exit unless user explicitly quits.
- **D-16:** Model: `claude-haiku-4-5-20251001`.
- **D-17:** System prompt: marker definitions + one short inline format example (~8-10 lines).
- **D-18:** Tone instruction: `"enthusiastic educator, direct, conversational English"`.
- **D-19:** System prompt must explicitly state word count target: 300-600 words.
- **D-20:** Cache: system prompt AND the assembled bootcamp transcript excerpts in `cache_control: {"type": "ephemeral"}`.
- **D-21:** Per-lesson call only sends: lesson outline + lesson title keywords (uncached).
- **D-22:** Use `anthropic.beta.prompt_caching` via Anthropic Python SDK with `model="claude-haiku-4-5-20251001"`.

### Claude's Discretion

- Exact system prompt wording (beyond the decisions above)
- Context assembly token budget calculation (how much of each transcript excerpt to include given model context)
- Error handling for missing ANTHROPIC_API_KEY
- `rich` panel/table styling details beyond what's specified above
- Temp file location for edit flow
- Slug generation logic for filenames

### Deferred Ideas (OUT OF SCOPE)

- Batch mode (generate all pending scripts automatically) — v2, BATCH-01
- Cost estimator before generation — v2, BATCH-03
- `--dry-run` flag (show context without calling API) — Phase 5 / WRK-04
- Word count / duration estimate in review display — v2, QUAL-03
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCRPT-01 | Interactive lesson selector — browse lessons by module, see pending/done status | Rich Table + IntPrompt pattern; `get_all()` provides status; module→lesson two-level navigation confirmed |
| SCRPT-02 | Context assembly — pull lesson outline + top-5 relevant bootcamp transcript segments | `find_relevant_transcripts(keywords, max_results=5, excerpt_chars=1500)` API confirmed; `get_lesson()` provides outline; token budget ~15K chars for 5 excerpts |
| SCRPT-03 | Claude API call (Anthropic SDK) — generates English narration script with markers | SDK 0.84.0 installed; `messages.create(system=[TextBlockParam...], model=..., messages=[...])` confirmed; no streaming needed |
| SCRPT-04 | Script review loop — display generated script, allow (a)ccept / (e)dit / (r)egenerate / (s)kip | `rich.syntax.Syntax` for display; `Prompt.ask()` for choices; `subprocess.run` for editor; temp file in project root or `/tmp` |
| SCRPT-05 | Save approved script to `scripts/M{n}L{n}_{slug}.md` | `SCRIPTS_DIR` from config; slug via `re.sub(r'[^a-z0-9]+', '_', title.lower())`; `set_status(lesson_id, "scripted")` API confirmed |
| SCRPT-06 | Prompt caching — system prompt + bootcamp index cached across generations | `TextBlockParam(type='text', text=..., cache_control={'type': 'ephemeral'})` confirmed working in SDK 0.84.0; `usage.cache_creation_input_tokens` and `usage.cache_read_input_tokens` available for verification |
</phase_requirements>

---

## Summary

Phase 3 builds three modules — `context_builder.py`, `script_generator.py`, `review_ui.py` — plus the `generate.py` entrypoint. All Phase 2 APIs are confirmed stable and ready to consume. The Anthropic SDK (0.84.0) is installed and fully supports prompt caching natively via `TextBlockParam` with `cache_control`; no `betas` header or `anthropic.beta.prompt_caching` namespace is required (decision D-22 uses an older nomenclature, but the mechanism is the same). `rich` 13.9.4 is installed with `Prompt`, `Table`, `Syntax`, `Panel` all available. `questionary` is NOT installed — navigation uses `rich.prompt.IntPrompt` + simple input loops.

The prompt caching architecture is clean: the system prompt (markers + format example + tone) is one cached `TextBlockParam`, and the assembled bootcamp excerpts (pre-built text string from `find_relevant_transcripts`) is a second cached block in the first user message. Only the lesson outline + title keywords are sent fresh per call. The usage response provides `cache_creation_input_tokens` and `cache_read_input_tokens` fields for cost monitoring.

The editor integration pattern (`$EDITOR` / `notepad` fallback via `subprocess.run`) is straightforward — write temp file, block on subprocess, read back, delete temp file. All slug generation should use `re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')` for safe filenames.

**Primary recommendation:** Use `TextBlockParam(cache_control={'type': 'ephemeral'})` natively in SDK 0.84.0 for system prompt caching. The `anthropic.beta.prompt_caching` import in D-22 does NOT exist in 0.84.0 — this is resolved by using `TextBlockParam` directly from `anthropic.types`.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| anthropic | 0.84.0 (installed) | Claude API calls + prompt caching | Only option; SDK version confirmed working |
| rich | 13.9.4 (installed) | Terminal tables, colored output, script display | Already in requirements.txt; all needed components verified |
| pathlib | stdlib | File I/O for script saving | Established pattern in project |
| subprocess | stdlib | Opening $EDITOR for script editing | Standard approach for CLI editor integration |
| re | stdlib | Slug generation, word count | No extra dep needed |
| tempfile | stdlib | Temp file location for edit flow | Cross-platform safe temp dir |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| os | stdlib | `os.environ.get("EDITOR", "notepad")` | Editor detection in D-12 |
| shlex | stdlib | Splitting EDITOR env var safely (e.g. `"code --wait"`) | When EDITOR has args |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `rich.prompt.IntPrompt` | `questionary` | questionary NOT installed; rich.prompt sufficient for numbered menus |
| `tempfile.mktemp()` | custom `tmp_{id}.md` | tempfile.gettempdir() is safer cross-platform; either works |

**Installation — nothing new needed:**
```bash
pip install anthropic  # already at 0.84.0
# rich already installed; all other deps are stdlib
```

**Version verification (confirmed 2026-03-26):**
- `anthropic`: 0.84.0 (pip show anthropic)
- `rich`: 13.9.4 (pip show rich)

---

## Architecture Patterns

### Recommended Project Structure

```
src/
├── context_builder.py     # lesson outline + transcript excerpt assembly
├── script_generator.py    # Claude API call, caching, response parsing
└── review_ui.py           # rich display, a/e/r/s loop, file save
generate.py                # entrypoint: imports and wires all three
scripts/                   # output: M{n}L{n}_{slug}.md
```

### Pattern 1: Prompt Caching with TextBlockParam (SDK 0.84.0)

**What:** Pass system prompt as a list of `TextBlockParam` objects with `cache_control`. The bootcamp excerpts go into the first user message content block, also marked for caching. Only lesson-specific content is uncached.

**When to use:** Always — caching amortizes the cost of the 7500-char transcript block across all 30 lesson generations.

**Example:**
```python
# Source: verified against anthropic SDK 0.84.0 installed locally
from anthropic import Anthropic
from anthropic.types import TextBlockParam

client = Anthropic()  # reads ANTHROPIC_API_KEY from env

SYSTEM_PROMPT = """You are an enthusiastic educator...[markers + example]..."""

def generate_script(lesson_outline: str, bootcamp_excerpts: str, revision_note: str = "") -> str:
    user_text = f"BOOTCAMP CONTEXT:\n{bootcamp_excerpts}\n\nLESSON OUTLINE:\n{lesson_outline}"
    if revision_note:
        user_text += f"\n\nRevision note: {revision_note}"

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        system=[
            TextBlockParam(
                type="text",
                text=SYSTEM_PROMPT,
                cache_control={"type": "ephemeral"},
            )
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": bootcamp_excerpts,
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": f"LESSON OUTLINE:\n{lesson_outline}",
                    },
                ],
            }
        ],
    )
    return response.content[0].text
```

**CRITICAL NOTE on D-22:** `anthropic.beta.prompt_caching` does NOT exist as an import in SDK 0.84.0. That module/namespace was removed when caching was promoted to stable. Use `TextBlockParam` from `anthropic.types` directly with `cache_control={"type": "ephemeral"}` — this is the correct 0.84.0 approach and achieves exactly what D-20/D-21 describe.

### Pattern 2: Two-Level Rich Interactive Menu

**What:** Module selection (numbered list) → lesson list within module (numbered list with status colors) → back navigation. Uses `rich.table.Table` for display, `rich.prompt.IntPrompt` for input.

**When to use:** Always — questionary is not installed, this is the only rich-native approach.

**Example:**
```python
# Source: rich 13.9.4 docs + local install verification
from rich.console import Console
from rich.table import Table
from rich.prompt import IntPrompt
from rich.text import Text

console = Console()

def pick_module(modules: list[dict]) -> dict | None:
    table = Table(title="Modules")
    table.add_column("#", style="bold")
    table.add_column("Module")
    for i, mod in enumerate(modules, 1):
        table.add_row(str(i), mod["title"])
    table.add_row("0", "Quit")
    console.print(table)
    choice = IntPrompt.ask("Select module", default=0)
    if choice == 0:
        return None
    return modules[choice - 1]
```

### Pattern 3: Status-Colored Lesson Table

**What:** Use `rich.text.Text` with per-cell styles for status column (yellow/green/blue).

**Example:**
```python
STATUS_STYLES = {
    "pending": "yellow",
    "scripted": "green",
    "audio_done": "blue",
}

def render_lesson_row(lesson_id: str, title: str, status: str) -> tuple:
    status_text = Text(status, style=STATUS_STYLES.get(status, "white"))
    return (lesson_id, title, status_text)
```

### Pattern 4: Editor Integration

**What:** Write script to temp file, block on subprocess, read back, delete.

**Example:**
```python
import os
import subprocess
import tempfile
from pathlib import Path

def open_in_editor(content: str) -> str:
    editor = os.environ.get("EDITOR", "notepad")
    # Handle EDITOR values like "code --wait"
    editor_parts = editor.split()

    with tempfile.NamedTemporaryFile(
        suffix=".md", mode="w", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        tmp_path = f.name

    try:
        subprocess.run(editor_parts + [tmp_path], check=True)
        return Path(tmp_path).read_text(encoding="utf-8")
    finally:
        Path(tmp_path).unlink(missing_ok=True)
```

### Pattern 5: Slug Generation

**What:** Convert lesson title to safe filename component.

**Example:**
```python
import re

def make_slug(title: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')

# "Character Bible" → "character_bible"
# "M0L3 — Tool Setup" → "m0l3_tool_setup"
```

### Pattern 6: Script Display with Syntax Highlighting

**What:** Use `rich.syntax.Syntax` to highlight production markers in terminal.

**Example:**
```python
from rich.syntax import Syntax
from rich.panel import Panel
from rich.console import Console

console = Console()

def display_script(script_text: str, lesson_title: str):
    # No built-in language for script format; use "markdown" for basic highlighting
    syntax = Syntax(script_text, "markdown", theme="monokai", word_wrap=True)
    console.print(Panel(syntax, title=lesson_title, border_style="cyan"))
```

### Anti-Patterns to Avoid

- **Importing `anthropic.beta.prompt_caching`:** This module does not exist in SDK 0.84.0. Use `TextBlockParam` from `anthropic.types` with `cache_control` directly.
- **Hardcoding word limits:** Always read from `config.SCRIPT_MIN_WORDS` / `config.SCRIPT_MAX_WORDS`.
- **Introducing classes:** All existing src modules use module-level functions only. Continue this pattern in `context_builder`, `script_generator`, `review_ui`.
- **Using `os.system()` for editor:** Use `subprocess.run()` — it blocks correctly and returns exit code.
- **Caching lesson-specific content:** Only cache system prompt + bootcamp excerpts. The lesson outline per D-21 must remain uncached.
- **Calling `find_relevant_transcripts()` inside the script generator:** This belongs in `context_builder.py` only.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Colored terminal output | Custom ANSI codes | `rich.text.Text(style=...)` | Already installed, handles Windows terminal |
| Numbered input menu | Custom input loop with validation | `rich.prompt.IntPrompt.ask()` | Built-in bounds validation, re-prompts on bad input |
| Word count check | Custom tokenizer | `len(script.split())` | Sufficient for 300-600 word target check |
| Temp file management | Manual path construction | `tempfile.NamedTemporaryFile` | Cross-platform, safe on Windows |
| API key error messages | Silent failure | `raise ValueError("ANTHROPIC_API_KEY not set...")` in script_generator init | Fail fast with actionable message |

**Key insight:** The `rich` library eliminates all custom terminal formatting code. The `anthropic` SDK eliminates all HTTP-level complexity for caching.

---

## Common Pitfalls

### Pitfall 1: Wrong Prompt Caching Import

**What goes wrong:** Code does `from anthropic.beta.prompt_caching import PromptCachingBetaMessageParam` or `client.beta.prompt_caching.messages.create(...)`. Both fail with `ImportError` / `AttributeError` in SDK 0.84.0.

**Why it happens:** Decision D-22 references `anthropic.beta.prompt_caching` which was the old API (pre-0.31). It was promoted to stable and is now done via `TextBlockParam(cache_control={"type": "ephemeral"})`.

**How to avoid:** Use `from anthropic.types import TextBlockParam` and set `cache_control={"type": "ephemeral"}` on the block. Confirmed working in 0.84.0.

**Warning signs:** `ImportError: cannot import name 'PromptCachingBeta...'`

### Pitfall 2: Cache Block Placement

**What goes wrong:** Putting the bootcamp excerpts in the system prompt instead of the first user message. OR putting them in the uncached part of the user message.

**Why it happens:** Uncertainty about where the second cache block goes.

**How to avoid:** Per Anthropic docs: system prompt = first cache breakpoint; first content block of first user message = second cache breakpoint (up to 4 breakpoints total supported). The bootcamp excerpts block must be the FIRST element in the user message `content` list with `cache_control`. The lesson outline block follows WITHOUT `cache_control`.

**Warning signs:** Response `usage.cache_read_input_tokens` always 0 after first call.

### Pitfall 3: EDITOR env var with arguments

**What goes wrong:** `subprocess.run(os.environ.get("EDITOR", "notepad"), ...)` fails when `EDITOR="code --wait"` because it tries to execute `"code --wait"` as a single command.

**How to avoid:** Split via `editor.split()` before constructing the command list: `editor_parts + [tmp_path]`. `shell=False` remains safe.

**Warning signs:** `FileNotFoundError: [WinError 2] The system cannot find the file specified: 'code --wait'`

### Pitfall 4: Blocking on subprocess on Windows

**What goes wrong:** `notepad.exe` on Windows may not block until the file is saved — it can return before the user closes the window in some environments.

**Why it happens:** `subprocess.run()` blocks on the process, but some editors spawn a child and exit the parent immediately.

**How to avoid:** For `notepad`, it does block correctly via `subprocess.run()`. For VS Code, `EDITOR="code --wait"` is the correct form. Document this in README. No code fix needed — just use `subprocess.run(..., check=False)` (don't raise on non-zero exit from the editor).

**Warning signs:** Script reads back immediately with original content unchanged.

### Pitfall 5: Missing ANTHROPIC_API_KEY at import time

**What goes wrong:** `Anthropic()` client is constructed at module level in `script_generator.py`. If the key is missing, it raises at import time, crashing the whole app before the menu renders.

**How to avoid:** Construct the client lazily inside `generate_script()`, or check for key at the start of `generate_script()` and raise a clear `ValueError` with instructions.

**Warning signs:** `anthropic.AuthenticationError` on startup.

### Pitfall 6: Token budget overflow

**What goes wrong:** 5 excerpts × 1500 chars each = 7500 chars (~1875 tokens) + system prompt + lesson outline. Haiku 4.5 has 200K context window — not a risk for generation. BUT the minimum cache block size is 1024 tokens. If the system prompt is too short (< 1024 tokens), it won't be cached.

**How to avoid:** Keep system prompt substantive (include marker definitions + format example = comfortably over 1024 tokens). The bootcamp excerpt block at ~1875 tokens is safely above the threshold.

**Warning signs:** `usage.cache_creation_input_tokens == 0` despite sending `cache_control`.

---

## Code Examples

### Full Prompt Caching Call (Verified Pattern)

```python
# Source: verified against anthropic 0.84.0 local install (2026-03-26)
from anthropic import Anthropic
from anthropic.types import TextBlockParam
from config import SCRIPT_MIN_WORDS, SCRIPT_MAX_WORDS, SCRIPT_STYLE

client = None  # lazy init

def _get_client() -> Anthropic:
    global client
    if client is None:
        import os
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Add it to your .env file."
            )
        client = Anthropic(api_key=key)
    return client


SYSTEM_PROMPT = f"""You are an {SCRIPT_STYLE} creating video lesson scripts.

FORMAT RULES:
- Each line is EITHER narration text OR a production marker on its own line.
- Production markers: [SCREEN RECORDING: description], [IMAGE: description],
  [VIDEO: description], [VO], [PAUSE]
- Target: {SCRIPT_MIN_WORDS}-{SCRIPT_MAX_WORDS} words of narration.
- No headers, no bullet points — just inline script format.

EXAMPLE (8-10 lines):
Welcome back. Today we're building your first consistent AI character.
[SCREEN RECORDING: Open Higgsfield homepage]
This is where everything starts — the DNA Triangulation method.
[IMAGE: Diagram showing three reference angles]
Here's what makes this different from everything you've tried before.
[VO]
You'll use three reference images, each from a different angle.
[PAUSE]
The result? A character that looks identical every single time.
[SCREEN RECORDING: Side-by-side comparison of consistent outputs]
"""


def generate_script(
    lesson_outline: str,
    bootcamp_excerpts: str,
    revision_note: str = "",
) -> str:
    """Call Claude with caching. Returns raw script text."""
    c = _get_client()

    user_content = [
        {
            "type": "text",
            "text": bootcamp_excerpts,
            "cache_control": {"type": "ephemeral"},  # second cache breakpoint
        },
        {
            "type": "text",
            "text": f"LESSON OUTLINE:\n{lesson_outline}"
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
                cache_control={"type": "ephemeral"},  # first cache breakpoint
            )
        ],
        messages=[{"role": "user", "content": user_content}],
    )

    # Optional: log cache stats
    u = response.usage
    print(
        f"  [cache] created={u.cache_creation_input_tokens} "
        f"read={u.cache_read_input_tokens} "
        f"in={u.input_tokens} out={u.output_tokens}"
    )

    return response.content[0].text
```

### Context Assembler

```python
# Source: based on verified Phase 2 APIs
from src.transcript_loader import find_relevant_transcripts
from src.course_loader import get_lesson
import re


def extract_keywords(lesson_title: str, lesson_content: str) -> list[str]:
    """Extract search keywords from lesson title and content."""
    # Use title words + first sentence of content
    combined = lesson_title + " " + lesson_content[:200]
    words = re.findall(r'\b[a-zA-Z]{4,}\b', combined)
    return list(dict.fromkeys(words))[:10]  # deduplicated, max 10


def assemble_context(module_num: str, lesson_num: str) -> dict:
    """
    Returns:
        {
            "lesson_outline": str,
            "bootcamp_excerpts": str,
            "lesson_id": str,
            "lesson_title": str,
        }
    """
    lesson = get_lesson(module_num, lesson_num)
    if not lesson:
        raise ValueError(f"Lesson not found: M{module_num}L{lesson_num}")

    keywords = extract_keywords(lesson["title"], lesson["content"])
    results = find_relevant_transcripts(keywords, max_results=5, excerpt_chars=1500)

    excerpt_parts = []
    for score, fname, excerpt in results:
        excerpt_parts.append(f"[Source: {fname}]\n{excerpt}")

    bootcamp_text = "\n\n---\n\n".join(excerpt_parts) if excerpt_parts else "(no relevant bootcamp transcripts found)"

    return {
        "lesson_id": lesson["id"],
        "lesson_title": lesson["title"],
        "lesson_outline": lesson["content"],
        "bootcamp_excerpts": bootcamp_text,
    }
```

### Script Save + Status Update

```python
# Source: config.py SCRIPTS_DIR verified; lesson_tracker.set_status() API confirmed
import re
from pathlib import Path
from config import SCRIPTS_DIR
from src.lesson_tracker import set_status


def make_slug(title: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')


def save_script(lesson_id: str, lesson_title: str, script_text: str) -> Path:
    slug = make_slug(lesson_title)
    filename = f"{lesson_id}_{slug}.md"
    path = SCRIPTS_DIR / filename
    path.write_text(script_text, encoding="utf-8")
    set_status(lesson_id, "scripted")
    return path
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `client.beta.prompt_caching.messages.create(betas=["prompt-caching-2024-07-31"])` | `TextBlockParam(cache_control={"type": "ephemeral"})` in standard `messages.create` | ~anthropic SDK 0.31 | D-22 references the old API — must use new approach |
| `anthropic.beta.prompt_caching.PromptCachingBetaTextBlockParam` | `anthropic.types.TextBlockParam` | ~anthropic SDK 0.31 | Same import path change |
| `questionary` for interactive menus | `rich.prompt.IntPrompt` | n/a — questionary not installed | Simpler, fewer deps |

**Deprecated/outdated:**
- `anthropic.beta.prompt_caching` namespace: removed from SDK; `TextBlockParam` is the current standard.
- D-22's reference to `anthropic.beta.prompt_caching` is stale naming for what is now native caching — the behavior it describes is correct, only the import path is wrong.

---

## Open Questions

1. **`claude-haiku-4-5-20251001` model ID validity**
   - What we know: This exact string appears in D-16/D-22. The SDK does not expose a models list constant to verify offline.
   - What's unclear: Whether this exact model ID string is valid (format looks correct for Claude naming conventions).
   - Recommendation: If the first API call fails with `model not found`, fall back to `claude-haiku-4-5` (shorter alias form). Add a note in generate.py comments.

2. **Minimum cacheable block size for system prompt**
   - What we know: Anthropic requires minimum 1024 tokens in a cache block for caching to activate. The system prompt with marker definitions + example is estimated ~250-350 tokens.
   - What's unclear: Whether combining system prompt + bootcamp excerpts in separate blocks satisfies the 1024 token minimum per block.
   - Recommendation: Move bootcamp excerpts to be the ONLY cached block (second breakpoint) if system prompt alone is under 1024 tokens. OR expand system prompt to include all marker docs verbosely. The 5-excerpt bootcamp block (~1875 tokens) definitely clears the threshold.
   - Alternative: Cache ONLY the bootcamp excerpts block (it's the expensive one) and leave system prompt as plain string. This is simpler and still captures 90% of the savings.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (installed, no config file — uses defaults) |
| Config file | none (conftest.py provides sys.path only) |
| Quick run command | `cd C:\Users\sahin\projects\course-production && python -m pytest tests/ -x -q` |
| Full suite command | `cd C:\Users\sahin\projects\course-production && python -m pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCRPT-01 | Module list returned from course_loader | unit | `python -m pytest tests/test_context_builder.py::test_list_modules -x` | ❌ Wave 0 |
| SCRPT-01 | Lesson list for a module includes id/title/status fields | unit | `python -m pytest tests/test_context_builder.py::test_lesson_list_fields -x` | ❌ Wave 0 |
| SCRPT-02 | assemble_context returns lesson_outline + bootcamp_excerpts | unit | `python -m pytest tests/test_context_builder.py::test_assemble_context_structure -x` | ❌ Wave 0 |
| SCRPT-02 | assemble_context calls find_relevant_transcripts with keywords | unit | `python -m pytest tests/test_context_builder.py::test_assemble_context_calls_transcripts -x` | ❌ Wave 0 |
| SCRPT-03 | generate_script raises ValueError if API key missing | unit | `python -m pytest tests/test_script_generator.py::test_missing_api_key -x` | ❌ Wave 0 |
| SCRPT-03 | generate_script builds correct message structure (mock client) | unit | `python -m pytest tests/test_script_generator.py::test_message_structure -x` | ❌ Wave 0 |
| SCRPT-04 | Review loop: (s)kip returns without saving | unit | `python -m pytest tests/test_review_ui.py::test_skip_does_not_save -x` | ❌ Wave 0 |
| SCRPT-04 | Review loop: (a)ccept calls save_script and set_status | unit | `python -m pytest tests/test_review_ui.py::test_accept_saves -x` | ❌ Wave 0 |
| SCRPT-05 | save_script writes file to SCRIPTS_DIR with correct name | unit | `python -m pytest tests/test_context_builder.py::test_save_script_path -x` | ❌ Wave 0 |
| SCRPT-05 | save_script calls set_status("scripted") | unit | `python -m pytest tests/test_context_builder.py::test_save_sets_status -x` | ❌ Wave 0 |
| SCRPT-06 | TextBlockParam cache_control accepted by SDK | unit | `python -m pytest tests/test_script_generator.py::test_cache_control_param -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python -m pytest tests/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_context_builder.py` — covers SCRPT-01, SCRPT-02, SCRPT-05 (file save/status)
- [ ] `tests/test_script_generator.py` — covers SCRPT-03, SCRPT-06 (mock Anthropic client)
- [ ] `tests/test_review_ui.py` — covers SCRPT-04 (mock console input, mock save_script)

*(tests/conftest.py already exists — no gap there)*

---

## Sources

### Primary (HIGH confidence)

- Anthropic SDK 0.84.0 — local install inspection via `python -c "import anthropic; ..."` — confirmed `TextBlockParam`, `CacheControlEphemeralParam`, `usage.cache_creation_input_tokens`, `usage.cache_read_input_tokens` fields
- `src/transcript_loader.py` — `find_relevant_transcripts(keywords, max_results=5, excerpt_chars=1500)` signature read directly
- `src/lesson_tracker.py` — `get_all()`, `get_status()`, `set_status()` API read directly
- `src/course_loader.py` — `load_course()`, `get_lesson()`, `list_all_lessons()` API read directly
- `config.py` — `SCRIPTS_DIR`, `SCRIPT_MIN_WORDS=300`, `SCRIPT_MAX_WORDS=600`, `SCRIPT_STYLE` confirmed
- `requirements.txt` — `rich>=13.0` confirmed; `anthropic` not yet in requirements.txt (needs adding)
- rich 13.9.4 — `from rich.prompt import Prompt, IntPrompt` and other components verified locally
- pytest — installed; `tests/conftest.py` adds sys.path; 18 existing tests pass in 0.34s

### Secondary (MEDIUM confidence)

- Anthropic prompt caching promotion from beta to stable — inferred from SDK inspection (no `beta.prompt_caching` namespace, `TextBlockParam.cache_control` accepted)

### Tertiary (LOW confidence)

- Minimum 1024 token cache block threshold — from training knowledge; not verified against official docs in this session. Flag for validation if caching shows 0 cached tokens.
- `claude-haiku-4-5-20251001` model ID exact string — not verified against live API; based on D-16/D-22 decisions.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries verified locally installed and functional
- Architecture: HIGH — all Phase 2 APIs read directly from source; caching verified against live SDK
- Pitfalls: HIGH (SDK import pitfall confirmed by inspection), MEDIUM (editor blocking behavior, cache threshold)

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (anthropic SDK is fast-moving; re-verify if upgraded)

**Critical note for planner:** `anthropic` is NOT in `requirements.txt` yet. Plan 3.2 must include a task to add `anthropic>=0.84.0` to requirements.txt.
