---
phase: 04-tts-audio-generator
plan: 02
subsystem: audio
tags: [kokoro, tts, wav, soundfile, numpy, chunking]

# Dependency graph
requires:
  - phase: 04-01
    provides: narration_extractor exports (extract_narration, find_script_path)
  - phase: 01-project-setup
    provides: config constants (AUDIO_DIR, KOKORO_VOICE_ID, KOKORO_LANG_CODE, KOKORO_SAMPLE_RATE)
provides:
  - src/audio_generator.py with generate_audio() and chunk_text() functions
  - Lazy KPipeline singleton (_get_pipeline) avoids repeated model loads
  - WAV output at 24000 Hz via soundfile to audio/M{m}L{l}_{slug}.wav
  - Unit test coverage with mocked KPipeline (no GPU needed in tests)
affects: [04-tts-audio-generator, 05-integrated-workflow]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Lazy singleton for expensive model initialization (KPipeline)"
    - "Text chunking at sentence boundaries via regex lookbehind (?<=[.!?])\s+"
    - "TDD: RED test commit then GREEN implementation commit"

key-files:
  created:
    - src/audio_generator.py
    - tests/test_audio_generator.py
  modified: []

key-decisions:
  - "chunk_text() defaults max_chars=2000 — fits Kokoro context safely while minimizing chunks"
  - "Lazy singleton pattern: _get_pipeline() loads model once on first generate_audio() call"
  - "output_path uses AUDIO_DIR module-level name — patchable in tests via patch('src.audio_generator.AUDIO_DIR')"

patterns-established:
  - "Singleton pattern: global _pipeline variable with None guard in _get_pipeline()"
  - "Sentence-boundary chunking: re.split(r'(?<=[.!?])\\s+', text) preserves complete sentences"

requirements-completed: [TTS-01, TTS-03, TTS-04]

# Metrics
duration: 8min
completed: 2026-03-27
---

# Phase 4 Plan 02: TTS Audio Generator Summary

**Kokoro KPipeline audio generator with sentence-boundary chunking, lazy singleton, and WAV output at 24000 Hz to audio/M{m}L{l}_{slug}.wav**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-27T07:00:00Z
- **Completed:** 2026-03-27T07:08:00Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 2

## Accomplishments

- generate_audio() converts narration text to WAV using Kokoro KPipeline with am_michael voice
- chunk_text() splits text >2000 chars at sentence boundaries — no mid-sentence cuts
- Lazy singleton _get_pipeline() loads the 82M model only once, reusing across calls
- 8 unit tests pass with mocked KPipeline — no GPU or model download needed in CI

## Task Commits

Each task was committed atomically (TDD pattern):

1. **Task 1 RED: Failing test stubs** - `28d48ed` (test)
2. **Task 1 GREEN: audio_generator implementation** - `698ee91` (feat)

_TDD task: test commit (RED) then implementation commit (GREEN)_

## Files Created/Modified

- `src/audio_generator.py` - generate_audio(), chunk_text(), _get_pipeline() singleton, Kokoro integration
- `tests/test_audio_generator.py` - 8 unit tests with mocked KPipeline covering all behaviors

## Decisions Made

- chunk_text() defaults max_chars=2000: safe Kokoro context limit, minimizes chunk overhead
- Lazy singleton: global `_pipeline` initialized on first call, suppresses warnings during load
- AUDIO_DIR patched at module level in tests — allows tmp_path injection without touching real filesystem

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- audio_generator.py exports generate_audio() and chunk_text() — ready for Phase 04-03 (CLI integration)
- Kokoro pipeline singleton tested end-to-end (test_tts.py previously validated GPU generation)
- No blockers for next plan

---
*Phase: 04-tts-audio-generator*
*Completed: 2026-03-27*
