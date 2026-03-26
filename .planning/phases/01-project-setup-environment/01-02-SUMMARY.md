---
plan: 01-02
phase: 01-project-setup-environment
status: complete
completed: 2026-03-26
---

# Summary: 01-02 — Kokoro TTS Verification & Unit Tests

## What Was Built

- **test_tts.py**: Smoke test that runs KPipeline with `am_michael`, concatenates chunks, writes `audio/test_output.wav`, asserts duration > 1s
- **tests/test_course_loader.py**: 6 tests — module loading, lesson count (33), `get_lesson` happy/sad path
- **tests/test_lesson_tracker.py**: 5 tests — default pending, set/get roundtrip, invalid status raises ValueError, get_all structure
- **tests/test_transcript_loader.py**: 4 tests — returns list, max_results respected, tuple structure, empty keywords
- **README.md**: Setup instructions, TTS verify step, pytest run, produce.py usage, project structure

## Key Files

key-files:
  created:
    - test_tts.py
    - tests/test_course_loader.py
    - tests/test_lesson_tracker.py
    - tests/test_transcript_loader.py
    - README.md

## Verification

`python -m pytest tests/ -v` → **15 passed** in 0.28s

## Deviations

- pytest wasn't on PATH (Windows Store Python) — ran as `python -m pytest` instead of `pytest` directly. Tests pass either way.
