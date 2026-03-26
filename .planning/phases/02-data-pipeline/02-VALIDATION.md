---
phase: 02
slug: data-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | none (conftest.py handles sys.path only) |
| **Quick run command** | `python -m pytest tests/ -v` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -v`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~1 second

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | DATA-01 | unit | `python -m pytest tests/test_transcript_loader.py -v` | ✅ | ⬜ pending |
| 02-01-02 | 01 | 1 | DATA-01 | unit | `python -m pytest tests/test_transcript_loader.py -v` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | DATA-03/04 | unit | `python -m pytest tests/test_lesson_tracker.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_transcript_loader.py::test_find_relevant_excerpt_chars` — DATA-01 configurable excerpt size
- [ ] `tests/test_transcript_loader.py::test_find_relevant_deterministic` — DATA-01 sort determinism
- [ ] `tests/test_lesson_tracker.py::test_init_idempotent` — DATA-03 idempotent init
- [ ] Fix `tests/test_lesson_tracker.py::test_set_status_valid` — tmp_path isolation instead of real file

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Status file persists across process restart | DATA-04 | Requires stopping/restarting Python process | `python -c "from src.lesson_tracker import set_status; set_status('M1L1','scripted')"` → restart Python → `python -c "from src.lesson_tracker import get_status; print(get_status('M1L1'))"` → should print `scripted` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 3s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
