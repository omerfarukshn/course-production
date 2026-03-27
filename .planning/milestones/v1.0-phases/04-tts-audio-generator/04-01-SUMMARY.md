---
phase: 04-tts-audio-generator
plan: 01
subsystem: tts
tags: [python, regex, pathlib, tts, narration, markdown]

# Dependency graph
requires:
  - phase: 03-script-generator
    provides: script .md files with [SCREEN RECORDING], [IMAGE], [VIDEO], [PAUSE], [VO] markers
provides:
  - extract_narration() strips headings and standalone markers from script .md files for clean TTS input
  - find_script_path() locates script files in SCRIPTS_DIR by lesson ID glob pattern
affects:
  - 04-tts-audio-generator (plan 02+) — uses extract_narration as input pipeline for Kokoro TTS

# Tech tracking
tech-stack:
  added: []
  patterns: [TDD red-green with pytest, regex marker stripping, pathlib glob for file lookup]

key-files:
  created:
    - src/narration_extractor.py
    - tests/test_narration_extractor.py
  modified: []

key-decisions:
  - "Marker regex ^\\[.+\\]$ matches standalone bracket lines exactly — inline markers within narration are preserved"
  - "Lines joined with single space (not newlines) for TTS — produces natural continuous speech"

patterns-established:
  - "Pattern 1: Standalone marker detection — re.match(r'^\\[.+\\]$', stripped) for exact bracket-only lines"
  - "Pattern 2: find_script_path uses SCRIPTS_DIR.glob(f'{lesson_id}_*.md') — consistent with save_script convention"

requirements-completed: [TTS-02]

# Metrics
duration: 2min
completed: 2026-03-26
---

# Phase 4 Plan 01: TTS Audio Generator — Narration Extractor Summary

**Narration extractor that strips [PAUSE], [VO], [SCREEN RECORDING:...], [IMAGE:...], [VIDEO:...] markers and headings from script .md files, outputting clean joined text for Kokoro TTS input**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-26T22:55:59Z
- **Completed:** 2026-03-26T22:57:24Z
- **Tasks:** 1 (TDD: RED + GREEN phases)
- **Files modified:** 2

## Accomplishments
- Created `extract_narration()` with regex-based stripping of all 5 marker types plus headings
- Created `find_script_path()` for lesson ID glob lookup in SCRIPTS_DIR
- 8 unit tests covering all TTS-02 behaviors — full suite 41/41 green, 0 regressions

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Failing tests for narration extractor** - `6d55562` (test)
2. **Task 1 GREEN: Narration extractor implementation** - `cccd7b0` (feat)

_Note: TDD tasks may have multiple commits (test -> feat -> refactor)_

## Files Created/Modified
- `src/narration_extractor.py` - extract_narration() and find_script_path() functions for TTS input pipeline
- `tests/test_narration_extractor.py` - 8 unit tests covering marker stripping, plain text preservation, and path lookup

## Decisions Made
- Marker regex `^\[.+\]$` strips standalone bracket lines only — inline markers embedded in narration are preserved (plan-specified behavior)
- Lines joined with single space rather than newlines — produces natural continuous speech flow for TTS

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `extract_narration()` ready to be wired into the TTS generation pipeline (plan 02+)
- `find_script_path()` provides lesson ID -> file path lookup for the audio generator
- Full test suite green at 41/41

---
*Phase: 04-tts-audio-generator*
*Completed: 2026-03-26*
