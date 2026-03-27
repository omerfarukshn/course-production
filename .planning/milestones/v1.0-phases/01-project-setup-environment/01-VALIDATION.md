---
phase: 1
slug: project-setup-environment
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Wave 0 installs) |
| **Config file** | `tests/conftest.py` (sys.path setup) |
| **Quick run command** | `python test_tts.py` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds (TTS init ~10s + unit tests ~5s) |

---

## Sampling Rate

- **After every task commit:** Run `python test_tts.py`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd:verify-work`:** Both test_tts.py and pytest tests/ must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | SETUP-01 | manual | `pip install -r requirements.txt` exits 0 | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 1 | SETUP-02 | smoke | `python test_tts.py` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | SETUP-03 | manual | `test -f README.md` | ❌ W0 | ⬜ pending |
| 1-02-01 | 02 | 1 | implicit | unit | `pytest tests/test_course_loader.py -x` | ❌ W0 | ⬜ pending |
| 1-02-02 | 02 | 1 | implicit | unit | `pytest tests/test_lesson_tracker.py -x` | ❌ W0 | ⬜ pending |
| 1-02-03 | 02 | 1 | implicit | unit | `pytest tests/test_transcript_loader.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/conftest.py` — sys.path setup so `from config import ...` works in all tests
- [ ] `tests/test_course_loader.py` — stubs for 33-lesson parse, get_lesson, list_all
- [ ] `tests/test_lesson_tracker.py` — stubs for init, get_status, set_status, get_all
- [ ] `tests/test_transcript_loader.py` — stubs for keyword search returns results
- [ ] `test_tts.py` — Kokoro am_michael smoke test
- [ ] `pip install pytest` — not yet in requirements.txt

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| requirements.txt installable cleanly | SETUP-01 | pip install output must be checked | `pip install -r requirements.txt` in fresh venv, verify no errors |
| README.md setup instructions accurate | SETUP-03 | Content correctness is subjective | Read README.md, follow steps, confirm setup works |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
