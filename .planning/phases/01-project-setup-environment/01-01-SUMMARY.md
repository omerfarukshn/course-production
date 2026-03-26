---
plan: 01-01
phase: 01-project-setup-environment
status: complete
completed: 2026-03-26
---

# Summary: 01-01 — Config Cleanup & Test Infrastructure

## What Was Built

Updated the project foundation to match the Kokoro TTS decision:

- **config.py**: Removed XTTS/TTS references (`TTS_REF_WAV`, `TTS_MODEL`, `TTS_LANGUAGE`), added `KOKORO_VOICE_ID="am_michael"`, `KOKORO_LANG_CODE="a"`, `KOKORO_SAMPLE_RATE=24000`
- **requirements.txt**: Replaced `TTS>=0.22.0` and `imageio[ffmpeg]>=2.34` with `kokoro>=0.9.4`, `soundfile`, `pytest`
- **.env.example**: Removed stale `TTS_REF_WAV` reference, added `KOKORO_VOICE_ID` comment
- **tests/conftest.py**: Created with `sys.path.insert(0, project_root)` for pytest
- **ROADMAP.md**: Already reflected correct decisions (Kokoro, Claude Code in-session, plan files listed)

## Key Files

key-files:
  created:
    - tests/conftest.py
    - .env.example
  modified:
    - config.py
    - requirements.txt
    - .planning/ROADMAP.md

## Verification

All acceptance criteria passed:
- `from config import KOKORO_VOICE_ID` → `am_michael` ✓
- No XTTS/TTS_MODEL/TTS_LANGUAGE refs in config.py ✓
- kokoro + soundfile + pytest in requirements.txt ✓
- No TTS>=0.22.0 in requirements.txt ✓
- tests/conftest.py with sys.path.insert ✓
- ROADMAP.md: 0 Chatterbox, 11 Kokoro, 1 Claude Code In-Session ✓

## Deviations

None — ROADMAP.md was already updated in planning phase, no re-work needed.
