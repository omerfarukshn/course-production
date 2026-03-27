# Retrospective: SahinLabs Course Production System

---

## Milestone: v1.0 — Production-Ready Script + Audio Generator

**Shipped:** 2026-03-27
**Phases:** 5 | **Plans:** 11 | **Timeline:** 2 days

### What Was Built

- Data pipeline: 98-file bootcamp transcript index + SahinLabs course content loader (33 lessons, M0–M5)
- Script generator: Claude API with TextBlockParam prompt caching, rich interactive review loop
- TTS pipeline: narration extractor + ElevenLabs Jon voice MP3 generation
- Unified CLI: `--lesson`, `--dry-run`, `--audio`, `--list` flags + startup status table
- 49 pytest tests, all mocked — no live API calls in test suite

### What Worked

- **Parallel worktree execution** (Wave 1 of Phase 5) — ElevenLabs migration and status table built simultaneously; saves real time
- **Plan-first approach** — Each phase had exact function signatures and code blocks in plans; implementation matched interfaces without integration surprises
- **Human verification gates** — Caught real issues (worktree file sync in Phase 4, Windows emoji encoding in Phase 5) that automated tests wouldn't catch
- **Prompt caching from day 1** — TextBlockParam pattern set up in Phase 3; ~$0.54 total Claude cost for 33 lessons
- **49 mocked tests** — Fast feedback without API cost; caught regressions at every phase

### What Was Inefficient

- **Phase 1 traceability gap** — SETUP-01/02/03 checked boxes never updated in REQUIREMENTS.md; caused false "incomplete" signal at milestone close
- **Worktree sync in Phase 4** — Parallel worktrees created files that didn't auto-merge; manual copy required. Plan should specify file sync steps explicitly
- **TTS pivot** — Kokoro fully built in Phase 4, then replaced by ElevenLabs in Phase 5. Could have decided on ElevenLabs earlier (GPU cost was known constraint)

### Patterns Established

- Lesson ID format: `M{module}L{lesson}` — e.g., M0L1, M1L3 — used everywhere in CLI and tracker
- Error pattern: `[red]❌ {what failed}. Fix: {what to do}[/red]` — consistent across all error paths
- Audio generation defaults to "n" — user explicitly opts in; prevents accidental credit spend
- Override guard before expensive API calls — check status, prompt for confirmation

### Key Lessons

1. **Decide TTS provider before building TTS** — GPU vs cloud API trade-off should be resolved in requirements, not mid-execution
2. **Explicit worktree merge steps in plans** — When parallel worktrees create new files, the merge plan must specify which files to sync and from where
3. **Update traceability as you go** — REQUIREMENTS.md checkboxes should be updated in each SUMMARY.md commit, not left for milestone close
4. **Dry-run mode is essential** — Add this from day 1 in any LLM-backed CLI; saves real iteration cost

### Cost Observations

- Model: Claude claude-sonnet-4-6 (all phases)
- Sessions: ~8 sessions across 2 days
- Notable: Prompt caching made 33-lesson production economically viable (~$0.54 total)

---

## Cross-Milestone Trends

| Metric | v1.0 |
|--------|------|
| Timeline | 2 days |
| Phases | 5 |
| Plans | 11 |
| LOC | 1,863 Python |
| Tests | 49 |
| Pivots | 1 (Kokoro → ElevenLabs) |
