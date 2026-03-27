---
phase: 05-integrated-workflow-polish
plan: 01
subsystem: audio
tags: [elevenlabs, tts, rest-api, requests, mp3, python]

# Dependency graph
requires:
  - phase: 04-tts-audio-generator
    provides: audio_generator.py with Kokoro backend and generate_audio() interface
provides:
  - ElevenLabs REST TTS backend replacing Kokoro
  - text_cleaner() for abbreviation expansion and whitespace normalization
  - MP3 output instead of WAV
  - Config constants for ElevenLabs (ELEVENLABS_VOICE_ID, ELEVENLABS_API_KEY, ELEVENLABS_MODEL_ID, ELEVENLABS_API_URL)
affects: [audio_entrypoint, generate]

# Tech tracking
tech-stack:
  added: [requests (already present), elevenlabs-rest-api]
  patterns: [REST API call with xi-api-key header, word-count-based duration estimation, text normalization before TTS]

key-files:
  created: []
  modified:
    - config.py
    - src/audio_generator.py
    - tests/test_audio_generator.py

key-decisions:
  - "ElevenLabs Jon voice (Cz0K1kOv9tD8l0b5Qu53) via eleven_turbo_v2_5 model — production quality, API key already available"
  - "Duration estimated from word count (150 wpm) since ElevenLabs REST does not return duration metadata"
  - "text_cleaner() normalizes abbreviations (e.g., vs., w/) and collapses whitespace before API call to improve TTS quality"
  - "Output format mp3_44100_128 — 128 kbps 44.1 kHz MP3, good quality for course audio"

patterns-established:
  - "requests.post with xi-api-key header pattern for ElevenLabs API calls"
  - "RuntimeError(f'ElevenLabs API error ({status_code})') as standard API error format"

requirements-completed: [TTS-05, WRK-01]

# Metrics
duration: 3min
completed: 2026-03-27
---

# Phase 5 Plan 01: ElevenLabs TTS Backend Summary

**Replaced Kokoro GPU-based TTS with ElevenLabs Jon REST API — MP3 output, text_cleaner with abbreviation expansion, RuntimeError on API failure, 49/49 tests green**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-03-27T00:08:47Z
- **Completed:** 2026-03-27T00:11:16Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Removed all Kokoro/numpy/soundfile GPU dependencies from audio_generator.py
- ElevenLabs REST API integration with Jon voice, stability=0.40, similarity_boost=0.88, style=0.15
- text_cleaner() expands abbreviations (e.g., vs., w/) and strips markdown/whitespace for cleaner TTS input
- Full test suite passes: 8 new ElevenLabs tests + 41 existing tests = 49 passed, 0 failed

## Task Commits

Each task was committed atomically:

1. **Task 1: Update config.py** - `37dd93a` (chore) — Remove Kokoro constants, add ELEVENLABS_* constants
2. **Task 2 RED: Failing tests** - `a289b75` (test) — 8 ElevenLabs test cases all failing before implementation
3. **Task 2 GREEN: Rewrite audio_generator.py** - `d3f0c52` (feat) — ElevenLabs backend, all 49 tests pass

_Note: TDD task has separate RED (test) and GREEN (feat) commits_

## Files Created/Modified

- `config.py` - Replaced KOKORO_* with ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL_ID, ELEVENLABS_API_URL
- `src/audio_generator.py` - Complete rewrite: text_cleaner(), generate_audio() via ElevenLabs REST, .mp3 output
- `tests/test_audio_generator.py` - Rewritten to mock requests.post instead of KPipeline; 8 tests

## Decisions Made

- ElevenLabs Jon voice (Cz0K1kOv9tD8l0b5Qu53) with eleven_turbo_v2_5 model — production audio quality without GPU dependency
- Duration estimated from word count at 150 wpm since the ElevenLabs REST API does not return timing metadata
- text_cleaner() normalizes input before API call to improve spoken quality (abbreviations, whitespace, markdown)
- Output format mp3_44100_128 (128 kbps 44.1 kHz MP3) — standard quality for course audio

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - TDD red-green cycle proceeded without issues. All 8 tests passed on first GREEN run.

## User Setup Required

**ELEVENLABS_API_KEY must be set in .env for audio generation to work.**

Add to `.env` in project root:
```
ELEVENLABS_API_KEY=sk_ef549d4112969ddba570634c0d57b14e2d2f708b0ced0a06
```

Verification:
```bash
python -c "from config import ELEVENLABS_API_KEY; print('Key set:', bool(ELEVENLABS_API_KEY))"
```

## Next Phase Readiness

- audio_generator.py now works without GPU — can run on any machine with internet access
- generate_audio() interface unchanged — audio_entrypoint.py requires no modification
- Remaining 05-integrated-workflow-polish plans can build on this foundation

---
*Phase: 05-integrated-workflow-polish*
*Completed: 2026-03-27*

## Self-Check: PASSED

- FOUND: src/audio_generator.py
- FOUND: config.py
- FOUND: tests/test_audio_generator.py
- FOUND: .planning/phases/05-integrated-workflow-polish/05-01-SUMMARY.md
- FOUND commit: 37dd93a (config.py update)
- FOUND commit: a289b75 (test RED)
- FOUND commit: d3f0c52 (implementation GREEN)
