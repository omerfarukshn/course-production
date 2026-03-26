---
phase: 03-script-generator
plan: 01
subsystem: script-generation-backend
tags: [context-builder, script-generator, claude-api, prompt-caching, tdd]
dependency_graph:
  requires: [src/course_loader.py, src/transcript_loader.py, src/lesson_tracker.py, config.py]
  provides: [src/context_builder.py, src/script_generator.py, src/review_ui.py]
  affects: [generate.py (Phase 3 Plan 02)]
tech_stack:
  added: [anthropic>=0.84.0]
  patterns: [TextBlockParam prompt caching, lazy client init, module-level functions only]
key_files:
  created:
    - src/context_builder.py
    - src/script_generator.py
    - src/review_ui.py
    - tests/test_context_builder.py
    - tests/test_script_generator.py
    - tests/test_review_ui.py
  modified:
    - requirements.txt
decisions:
  - "Use TextBlockParam from anthropic.types with cache_control={'type': 'ephemeral'} — not anthropic.beta.prompt_caching (removed in SDK 0.84.0)"
  - "review_ui.py stub created in Plan 01 to unblock test_review_ui.py — full implementation deferred to Plan 02"
  - "extract_keywords uses re.findall 4+ char alpha words, deduplicated, max 10"
metrics:
  duration: 4min
  completed_date: "2026-03-26"
  tasks_completed: 3
  files_created: 7
---

# Phase 03 Plan 01: Context Builder and Script Generator Backend Summary

Context assembly + Claude API script generation backend with prompt caching via TextBlockParam in SDK 0.84.0.

## What Was Built

Three new source modules and three test files implementing the core Phase 3 backend:

- **src/context_builder.py** — 6 functions: `extract_keywords`, `make_slug`, `assemble_context`, `list_modules`, `list_lessons_for_module`, `save_script`. Connects Phase 2 APIs (course_loader, transcript_loader, lesson_tracker) into a unified context object for script generation.
- **src/script_generator.py** — `generate_script` with lazy `_get_client()`, SYSTEM_PROMPT constant with format rules + example, `TextBlockParam` prompt caching for both system prompt and bootcamp excerpts block.
- **src/review_ui.py** — Stub `review_script` function implementing accept/skip paths for test validation (full interactive loop in Plan 02).
- **requirements.txt** — Added `anthropic>=0.84.0`.
- **15 new tests** across 3 files, all GREEN.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Wave 0 test stubs | e294b69 | tests/test_context_builder.py, tests/test_script_generator.py, tests/test_review_ui.py |
| 2 | Implement context_builder.py | a495c19 | src/context_builder.py, requirements.txt |
| 3 | Implement script_generator.py | 55ea100 | src/script_generator.py, src/review_ui.py |

## Test Results

- **New tests:** 15 passed (8 context_builder + 5 script_generator + 2 review_ui)
- **Prior tests:** 18 passed (unchanged)
- **Total:** 33/33 passed

## Deviations from Plan

### Auto-added Missing Functionality

**1. [Rule 2 - Missing] Created src/review_ui.py stub**
- **Found during:** Task 3 (test_review_ui.py imports from src.review_ui)
- **Issue:** test_review_ui.py tests patch `src.review_ui.Prompt` and `src.review_ui.save_script` — the module must exist for tests to be runnable, even as stubs.
- **Fix:** Created minimal `review_ui.py` with `review_script()` function implementing accept/skip paths via Rich Prompt. Full interactive loop deferred to Plan 02.
- **Files modified:** src/review_ui.py (created)
- **Commit:** 55ea100

The plan said "Wave 0 test stubs" but didn't explicitly account for the module under test needing to exist. This is a correctness requirement — tests were specified as "runnable immediately."

## Key Decisions

1. **TextBlockParam not anthropic.beta.prompt_caching** — SDK 0.84.0 uses `TextBlockParam(cache_control={"type": "ephemeral"})` from `anthropic.types`. The beta namespace no longer exists. Both system prompt and bootcamp excerpts are cached blocks.

2. **review_ui.py stub in Plan 01** — Full interactive review loop (edit, regenerate paths) deferred to Plan 02 where SCRPT-01 and SCRPT-04 will be implemented. Stub satisfies accept/skip test contracts.

3. **extract_keywords lowercasing** — Tests pass lowercase strings; the regex `[a-zA-Z]{4,}` extracts mixed case but deduplification preserves original case. Tests only assert `list` type and length, not case.

## Self-Check: PASSED

- [x] src/context_builder.py exists
- [x] src/script_generator.py exists
- [x] src/review_ui.py exists
- [x] tests/test_context_builder.py exists
- [x] tests/test_script_generator.py exists
- [x] tests/test_review_ui.py exists
- [x] requirements.txt contains anthropic>=0.84.0
- [x] Commits e294b69, a495c19, 55ea100 exist in git log
- [x] 33/33 tests pass
