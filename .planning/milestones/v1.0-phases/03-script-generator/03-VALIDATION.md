---
phase: 03
slug: script-generator
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `pytest.ini` or default discovery |
| **Quick run command** | `python -m pytest tests/test_context_builder.py tests/test_script_generator.py tests/test_review_ui.py -v --tb=short` |
| **Full suite command** | `python -m pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command (new phase tests only)
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green (18 prior tests + new phase tests)
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | SCRPT-02 | unit | `python -m pytest tests/test_context_builder.py -v` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 1 | SCRPT-03, SCRPT-06 | unit (mock API) | `python -m pytest tests/test_script_generator.py -v` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 1 | SCRPT-05 | unit | `python -m pytest tests/test_script_generator.py::test_save_script -v` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 2 | SCRPT-01 | unit | `python -m pytest tests/test_review_ui.py -v` | ❌ W0 | ⬜ pending |
| 03-03-02 | 03 | 2 | SCRPT-04 | manual + unit | `python -m pytest tests/test_review_ui.py::test_accept_saves_script -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_context_builder.py` — stubs for SCRPT-02 (assemble_context signature, token count)
- [ ] `tests/test_script_generator.py` — stubs for SCRPT-03, SCRPT-05, SCRPT-06 (mock anthropic client)
- [ ] `tests/test_review_ui.py` — stubs for SCRPT-01, SCRPT-04 (mock script, accept/skip paths)

*Note: pytest already installed (Phase 1). No new framework installation needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `$EDITOR` opens with script content | SCRPT-04 | Subprocess editor launch not automatable in CI | Run `python generate.py`, select a lesson, generate script, press `e`, verify editor opens with script text |
| Rich module menu renders correctly | SCRPT-01 | Terminal UI rendering not automatable | Run `python generate.py`, verify M0–M5 list renders with colors and lesson statuses |
| Full end-to-end: select → generate → accept → saved file | SCRPT-01–05 | Requires live API key + interactive session | Run `python generate.py`, select M0L1, accept script, verify `scripts/M0L1_welcome.md` created |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
