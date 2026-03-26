---
phase: 4
slug: tts-audio-generator
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-27
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none (uses existing conftest.py) |
| **Quick run command** | `python -m pytest tests/test_narration_extractor.py tests/test_audio_generator.py -q --tb=short` |
| **Full suite command** | `python -m pytest tests/ -q --tb=short` |
| **Estimated runtime** | ~5 seconds (unit tests only, no actual TTS calls) |

---

## Sampling Rate

- **After every task commit:** Run quick command above
- **After every plan wave:** Run full suite
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | TTS-02 | unit | `python -m pytest tests/test_narration_extractor.py -q` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 2 | TTS-03 | unit (mocked) | `python -m pytest tests/test_audio_generator.py -q` | ❌ W0 | ⬜ pending |
| 04-03-01 | 03 | 2 | TTS-04, TTS-05 | integration + manual | `python -m pytest tests/ -q` + manual listen | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_narration_extractor.py` — stubs for TTS-02 (script parsing, marker stripping)
- [ ] `tests/test_audio_generator.py` — stubs for TTS-03 (chunking, concatenation, mocked KPipeline)

*Existing `tests/conftest.py` infrastructure covers shared fixtures.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Audio sounds natural (am_michael voice) | TTS-05 | Subjective audio quality — not automatable | Play generated WAV, confirm voice is clear and natural |
| Audio duration ±15% of word-count estimate | TTS-05 | Requires actual Kokoro inference (GPU) | Check printed duration vs expected (300 words ≈ 90s) |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
