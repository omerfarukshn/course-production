---
phase: 04-tts-audio-generator
plan: 03
subsystem: tts-audio-generator
tags: [tts, audio, entrypoint, generate, kokoro, argparse]
dependency_graph:
  requires: [04-01, 04-02]
  provides: [audio_entrypoint, generate_audio_cli]
  affects: [generate.py, src/audio_entrypoint.py]
tech_stack:
  added: [argparse]
  patterns: [orchestrator-function, status-guard, quality-stats]
key_files:
  created: [src/audio_entrypoint.py]
  modified: [generate.py]
decisions:
  - "run_audio_generation() checks status guard first — rejects lessons without approved script"
  - "Slug extracted from script filename stem (split on first underscore)"
  - "Word-count ratio uses 2.5 words/sec (150 wpm) as expected speech rate"
  - "Quality warning fires if ratio is outside 0.85-1.15 range (+/-15%)"
  - "parse_known_args() used so --audio doesn't conflict with existing interactive args"
  - "audio_generator.py, course_loader.py, lesson_tracker.py copied from parallel worktrees (plan 04-02 ran on worktree-agent-a956cd10)"
metrics:
  duration: 12min
  completed: "2026-03-27"
  tasks_completed: 1
  tasks_total: 2
  files_changed: 7
---

# Phase 04 Plan 03: Audio Entrypoint + generate.py --audio Flag Summary

**One-liner:** `generate.py --audio LESSON_ID` orchestrates full TTS pipeline: status guard, script lookup, narration extraction, Kokoro WAV generation, quality stats, and play/skip prompt.

## What Was Built

### src/audio_entrypoint.py

`run_audio_generation(lesson_id: str)` orchestrates the complete audio pipeline:

1. Status guard — rejects if lesson is not `scripted`
2. Script lookup via `find_script_path(lesson_id)`
3. Narration extraction via `extract_narration(script_path)`
4. Slug derivation from script filename stem
5. Kokoro TTS via `generate_audio(lesson_id, narration, slug)`
6. Quality stats: duration, file size, word-count ratio (150 wpm baseline)
7. Warning if ratio is outside +/-15%
8. (p)lay / (s)kip prompt — opens audio with system default player on Windows
9. Status update to `audio_done`

### generate.py

Added `argparse` with `--audio LESSON_ID` flag using `parse_known_args()`. When `--audio` is supplied, calls `run_audio_generation()` and exits. Interactive flow unchanged when no args given.

## Verification Results

- `python generate.py --help` shows `--audio LESSON_ID` option
- `python -c "from src.audio_entrypoint import run_audio_generation; print('import OK')"` passes
- All 41 existing tests pass (no regressions)
- All acceptance criteria grep checks pass

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Missing files from parallel worktree**
- **Found during:** Task 1 setup
- **Issue:** Plan 04-02 ran in worktree `agent-a956cd10` and created `src/audio_generator.py`, `src/course_loader.py`, `src/lesson_tracker.py`, `src/__init__.py` — none were present in this worktree (`agent-a3fb786a`). Also `src/review_ui.py` was the stub version (plan 03-01) not the full version (plan 03-02).
- **Fix:** Copied the files directly from the parallel worktree and main project paths
- **Files modified:** `src/audio_generator.py` (copied), `src/course_loader.py` (copied), `src/lesson_tracker.py` (copied), `src/__init__.py` (copied), `src/review_ui.py` (updated)
- **Commit:** 6c7d70d

## Tasks Status

| Task | Name | Status | Commit |
|------|------|--------|--------|
| 1 | Create audio_entrypoint.py and wire generate.py --audio flag | Done | 6c7d70d |
| 2 | Verify actual audio generation on M0L1 | Awaiting human verification | — |

## Self-Check: PASSED

- `src/audio_entrypoint.py` exists: FOUND
- `generate.py` contains `import argparse`: FOUND
- `generate.py` contains `from src.audio_entrypoint import run_audio_generation`: FOUND
- `generate.py` contains `--audio`: FOUND
- Commit `6c7d70d` exists: FOUND
