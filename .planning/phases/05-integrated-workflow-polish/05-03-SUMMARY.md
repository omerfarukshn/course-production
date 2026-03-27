---
phase: 05-integrated-workflow-polish
plan: "03"
subsystem: cli
tags: [generate.py, argparse, dry-run, lesson-flow, retry, actionable-errors, rich]

# Dependency graph
requires:
  - phase: 05-integrated-workflow-polish
    plan: "01"
    provides: ElevenLabs TTS backend (audio_entrypoint, tts_client)
  - phase: 05-integrated-workflow-polish
    plan: "02"
    provides: startup status table, --list flag, show_status_table()
provides:
  - "--lesson LESSON_ID flag: full end-to-end flow (context → script → review → audio prompt)"
  - "--dry-run LESSON_ID flag: prints assembled context + token estimate, zero API calls"
  - "parse_lesson_id() helper: parses M0L1 format, raises ValueError on bad input"
  - "generate_script_with_retry(): one automatic retry on Claude API error with 10s delay"
  - "run_lesson_flow(): orchestrates all pipeline stages from a single lesson ID"
  - "run_dry_run(): offline context inspection tool"
  - "Actionable error messages with 'Fix:' guidance throughout generate.py"
affects: [future phases using generate.py CLI, any onboarding docs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "parse-then-dispatch pattern: argparse flags checked in main(), dispatch to dedicated functions"
    - "retry-on-API-error: catch anthropic.APIError, sleep 10s, single retry, then surface with context dump"
    - "actionable errors: every exception message includes 'Fix:' with next step"
    - "override guard: check lesson status before expensive API calls, prompt for confirmation"

key-files:
  created: []
  modified:
    - generate.py

key-decisions:
  - "parse_lesson_id() uses regex M(\\d+)L(\\d+) — strict format prevents silent misrouting to wrong lesson"
  - "Retry delay is 10s (not exponential) — simple, predictable, sufficient for transient Claude API errors"
  - "Dry-run truncates bootcamp excerpts to 2000 chars in display — avoids terminal flood while still showing content"
  - "Audio prompt defaults to 'n' — prevents accidental ElevenLabs credits spend during script iteration"

patterns-established:
  - "Lesson ID format: M{module}L{lesson} e.g. M0L1, M1L3 — used everywhere in CLI and tracker"
  - "Error pattern: '[red]❌ {what failed}. Fix: {what to do}[/red]' — consistent across all error paths"

requirements-completed: [WRK-02, WRK-03, WRK-04]

# Metrics
duration: 35min
completed: 2026-03-27
---

# Phase 05 Plan 03: Unified --lesson/--dry-run Flow Summary

**Single-command lesson production via `--lesson M0L1` (context → script → review → audio) and offline context inspection via `--dry-run M0L1`, with Claude API retry and actionable error messages throughout**

## Performance

- **Duration:** ~35 min (including human verification checkpoint)
- **Started:** 2026-03-27T09:14:00Z
- **Completed:** 2026-03-27T09:49:00Z
- **Tasks:** 1 auto + 1 checkpoint (human-verify, approved)
- **Files modified:** 1

## Accomplishments

- Added `--lesson LESSON_ID` flag: assembles context, generates script via Claude, runs review loop, prompts for audio generation in one command
- Added `--dry-run LESSON_ID` flag: prints lesson outline + bootcamp excerpts + token estimate without any API calls — zero cost debugging
- Added `parse_lesson_id()` with strict regex validation and clear error on bad format
- Added `generate_script_with_retry()`: catches `anthropic.APIError`, waits 10s, retries once, then saves context to `temp_context.txt` with actionable error
- Override guard: if lesson already `scripted` or `audio_done`, warns user and prompts before regenerating
- All error paths include `Fix:` with a specific next step

## Task Commits

Each task was committed atomically:

1. **Task 1: Add --lesson and --dry-run flags with full unified flow** - `8148019` (feat)

**Plan metadata:** (docs commit — this summary)

## Files Created/Modified

- `generate.py` - Added `--lesson`, `--dry-run` argparse flags; `parse_lesson_id()`, `generate_script_with_retry()`, `run_lesson_flow()`, `run_dry_run()` functions; updated `main()` dispatch; actionable error messages throughout

## Decisions Made

- Used strict regex `M(\d+)L(\d+)` for lesson ID parsing — rejects ambiguous input immediately rather than silently routing to wrong lesson
- Retry delay is fixed 10s (not exponential backoff) — simple and sufficient for transient Claude API rate limits; exponential not warranted for single retry
- Dry-run truncates displayed bootcamp excerpts at 2000 chars — prevents terminal flood, still shows enough to debug context issues
- Audio generation defaults to "n" prompt — prevents accidental ElevenLabs credit usage when user is iterating on script quality

## Deviations from Plan

None — plan executed exactly as written. All 49 pytest tests passed before and after implementation.

## Issues Encountered

None. The plan provided exact function signatures and code blocks; implementation matched interfaces from prior phases (context_builder, script_generator, audio_entrypoint, lesson_tracker) without integration issues.

## User Setup Required

None — no new external services or environment variables required. ElevenLabs API key was already set in Plan 01.

## Next Phase Readiness

Phase 05 (all 3 plans) is now complete. The full production pipeline is operational:

- `python generate.py` — interactive mode with status table on startup
- `python generate.py --list` — status table only
- `python generate.py --lesson M0L1` — full single-lesson production
- `python generate.py --dry-run M0L1` — offline context inspection
- `python generate.py --audio M0L1` — audio-only re-generation

Ömer can now produce any of the 33 lessons with one command. No blockers.

---
*Phase: 05-integrated-workflow-polish*
*Completed: 2026-03-27*
