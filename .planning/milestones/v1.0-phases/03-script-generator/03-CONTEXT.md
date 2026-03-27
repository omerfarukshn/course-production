# Phase 3: Script Generator - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Interactive lesson selection (rich terminal menu) → context assembly (lesson outline + top-5 bootcamp transcript excerpts) → Claude API script generation → review/edit loop → save approved script.

Phase delivers: `src/context_builder.py`, `src/script_generator.py`, `src/review_ui.py`, and the entrypoint `generate.py`. Does NOT include TTS audio (Phase 4) or full workflow orchestration (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Script Format
- **D-01:** Inline marker format (single column) — NOT two-column AV table.
- **D-02:** Each line is either narration text or a production marker on its own line.
- **D-03:** Markers: `[SCREEN RECORDING: description]`, `[IMAGE: description]`, `[VIDEO: description]`, `[VO]`, `[PAUSE]`.
- **D-04:** Target length: 300-600 words (as defined in `config.py`: `SCRIPT_MIN_WORDS=300`, `SCRIPT_MAX_WORDS=600`). Do NOT change these constants.
- **D-05:** Saved as `scripts/M{n}L{n}_{slug}.md` — Markdown file, inline format, no extra headers needed beyond lesson title.

Example of correct format:
```
Welcome back, everyone. Today we're building your first consistent AI character.
[SCREEN RECORDING: Open Higgsfield homepage]
This is where everything starts — the DNA Triangulation method.
[IMAGE: Diagram showing three reference angles]
Here's what makes this approach different from everything else you've tried.
[VO]
You're going to use three reference images from different angles...
[PAUSE]
```

### Lesson Selector UX
- **D-06:** Rich interactive menu — NOT CLI argument. Run with `python generate.py`, no args needed.
- **D-07:** Module selection first (M0–M5), then lesson list within that module.
- **D-08:** Each lesson row shows: `{ID} | {Title} | {status}` — e.g., `M1L1 | Character Bible | pending`.
- **D-09:** Status colors via `rich`: pending = yellow, scripted = green, audio_done = blue.
- **D-10:** User can navigate back to module list from lesson list.

### Script Review Flow
- **D-11:** `(a)ccept` — save script to `scripts/M{n}L{n}_{slug}.md`, mark status `scripted`, return to lesson selector.
- **D-12:** `(e)dit` — write script to temp `.md` file, open with `$EDITOR` (fallback: `notepad` on Windows), read back after editor closes, re-display modified script, ask accept/discard.
- **D-13:** `(r)egenerate` — prompt user for a note ("Regenerate with note: "), append note to Claude user message as `"\n\nRevision note: {note}"`, call API again, display new script.
- **D-14:** `(s)kip` — do nothing, return to lesson selector (status stays `pending`).
- **D-15:** After accept: immediately return to module selector (continuous flow). No exit unless user explicitly quits.

### Claude Model & System Prompt
- **D-16:** Model: `claude-haiku-4-5-20251001` — fastest, cheapest, sufficient quality.
- **D-17:** System prompt content: marker definitions + one short inline format example (NOT a full lesson script). The example should be ~8-10 lines demonstrating alternation between VO lines and markers.
- **D-18:** Tone instruction in system prompt: `"enthusiastic educator, direct, conversational English"` (matches existing `SCRIPT_STYLE` in config.py).
- **D-19:** System prompt must explicitly state word count target: 300-600 words.

### Prompt Caching Strategy (SCRPT-06)
- **D-20:** Cache: system prompt (marker definitions + format example + tone) AND the assembled bootcamp transcript excerpts in a `cache_control: {"type": "ephemeral"}` block.
- **D-21:** Per-lesson call only sends: lesson outline + lesson title keywords (uncached). Everything else is served from cache.
- **D-22:** Use `anthropic.beta.prompt_caching` via the Anthropic Python SDK with `model="claude-haiku-4-5-20251001"`.

### Claude's Discretion
- Exact system prompt wording (beyond the decisions above)
- Context assembly token budget calculation (how much of each transcript excerpt to include given model context)
- Error handling for missing ANTHROPIC_API_KEY
- `rich` panel/table styling details beyond what's specified above
- Temp file location for edit flow
- Slug generation logic for filenames

</decisions>

<specifics>
## Specific Ideas

- The lesson selector should feel like a simple interactive CLI, not a complex TUI. `rich` for display (colors, tables), but navigation is simple numbered input or arrow keys via `questionary` or `rich.prompt`.
- For the editor flow: write to `tmp_{lesson_id}.md`, open via `subprocess.run([os.environ.get("EDITOR", "notepad"), tmp_file])`, then read back. Delete temp file after.
- `rich` is already in `requirements.txt`. Use it for the lesson table and script display (syntax highlighting for markers).
- The bootcamp index cached in the prompt should be the pre-assembled excerpt text (result of `find_relevant_transcripts()` for the lesson's keywords), not the raw JSON. Cache the compiled text block.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project requirements and scope
- `.planning/REQUIREMENTS.md` — SCRPT-01 through SCRPT-06 definitions (requirements this phase covers)
- `.planning/PROJECT.md` — Core value, constraints, out-of-scope items

### Existing Phase 2 interfaces (Phase 3 consumes these)
- `src/transcript_loader.py` — `find_relevant_transcripts(keywords, max_results=5, excerpt_chars=1500)` signature; planner must use this exact API
- `src/lesson_tracker.py` — `get_all()`, `get_status(lesson_id)`, `set_status(lesson_id, status)` APIs; Phase 3 calls `set_status(lesson_id, "scripted")` after accept
- `src/course_loader.py` — lesson outline and keyword extraction source
- `config.py` — `SCRIPTS_DIR`, `ANTHROPIC_API_KEY` (via env), `SCRIPT_MIN_WORDS=300`, `SCRIPT_MAX_WORDS=600`, `SCRIPT_STYLE`

### Roadmap
- `.planning/ROADMAP.md` — Phase 3 plan breakdown (Context Assembler, Claude Script Generator, Script Review CLI)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/transcript_loader.find_relevant_transcripts()` — ready with `excerpt_chars=1500`; context_builder calls this directly
- `src/lesson_tracker.get_all()` / `set_status()` — status read/write, Phase 3 uses as-is
- `config.py` constants — `SCRIPTS_DIR`, `SCRIPT_MIN_WORDS`, `SCRIPT_MAX_WORDS`, `SCRIPT_STYLE` — use these, do not hardcode

### Established Patterns
- All src modules use simple module-level functions (no classes) — continue this pattern
- Config via `config.py` import, not argparse config
- JSON persistence via `pathlib.Path.read_text/write_text`
- `rich` already in requirements.txt

### Integration Points
- `generate.py` (new entrypoint) imports `context_builder`, `script_generator`, `review_ui`
- `context_builder.py` imports `course_loader` + `transcript_loader`
- `script_generator.py` imports `anthropic` SDK + `config`
- `review_ui.py` imports `rich` + `lesson_tracker` + `script_generator`

</code_context>

<deferred>
## Deferred Ideas

- Batch mode (generate all pending scripts automatically) — v2, BATCH-01
- Cost estimator before generation — v2, BATCH-03
- `--dry-run` flag (show context without calling API) — Phase 5 / WRK-04
- Word count / duration estimate in review display — v2, QUAL-03

</deferred>

---

*Phase: 03-script-generator*
*Context gathered: 2026-03-26*
