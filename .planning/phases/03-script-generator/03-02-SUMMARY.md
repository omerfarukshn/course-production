---
phase: 03-script-generator
plan: "02"
subsystem: script-generator
tags: [review-ui, rich-terminal, entrypoint, interactive]
dependency_graph:
  requires: ["03-01"]
  provides: ["generate.py entrypoint", "review_ui.py full implementation"]
  affects: ["src/review_ui.py", "generate.py"]
tech_stack:
  added: []
  patterns: ["rich terminal menus", "outer/inner navigation loop", "lazy error handling per deviation rules"]
key_files:
  created:
    - generate.py
  modified:
    - src/review_ui.py
decisions:
  - "After accept, break inner loop back to module selector (D-15) — not back to lesson selector"
  - "display_script import excluded from generate.py (review_ui.py calls it internally)"
  - "ValueError and generic Exception handled in generate.py main loop; KeyboardInterrupt returns immediately"
metrics:
  duration: "5min"
  completed_date: "2026-03-27"
  tasks_completed: 2
  tasks_total: 3
  files_changed: 2
---

# Phase 03 Plan 02: Review UI + generate.py Entrypoint Summary

**One-liner:** Rich terminal UI with module/lesson selector tables, full (a)ccept/(e)dit/(r)egenerate/(s)kip review loop, and `generate.py` entrypoint wiring context_builder + script_generator + review_ui.

## What Was Built

### Task 1: src/review_ui.py (full implementation)

Task 1 was already complete when this execution began. The full implementation includes:

- `show_module_menu()` — Rich `Table` with numbered module list (0 = Quit)
- `show_lesson_menu(module)` — Rich `Table` with color-coded status (yellow=pending, green=scripted, blue=audio_done)
- `display_script(script_text, lesson_title)` — Syntax-highlighted Panel with word count
- `open_in_editor(content)` — Opens `$EDITOR` (fallback: notepad) via tempfile, cleans up in finally
- `review_script(...)` — Full (a)/(e)/(r)/(s) loop with save_script + generate_script integration

### Task 2: generate.py (created)

Main entrypoint at project root (`C:/Users/sahin/projects/course-production/generate.py`):

- Outer loop: `show_module_menu()` — Quit (0) breaks out with "Goodbye!"
- Inner loop: `show_lesson_menu(module)` — Back (0) returns to module selector
- Generate + review: `assemble_context(module["num"], lesson["lesson_num"])` -> `generate_script(...)` -> `review_script(...)`
- After accept (returns True): breaks inner loop back to module selector (D-15 compliant)
- After skip (returns False): stays in inner loop (re-shows lesson selector)
- Error handling: ValueError, KeyboardInterrupt, Exception all handled gracefully

### Task 3: Human Verification Checkpoint (PENDING)

Task 3 is a `checkpoint:human-verify` — requires running `python generate.py` interactively with ANTHROPIC_API_KEY set to verify the full end-to-end flow.

## Deviations from Plan

None — plan executed exactly as written. The task prompt specified slightly different content for generate.py (omitting `display_script` import), and the final file matches that specification since `display_script` is called internally by `review_ui.py`, not by `generate.py` directly.

## Self-Check

**generate.py exists:** `C:/Users/sahin/projects/course-production/generate.py` — FOUND
**Import check:** `python -c "from generate import main"` — PASSED (verified above)
**Commit hash d45c9d3:** feat(03-02): create generate.py main entrypoint — FOUND

## Self-Check: PASSED
