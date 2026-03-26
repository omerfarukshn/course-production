# Roadmap: SahinLabs Course Production System

**Created:** 2026-03-26
**Milestone:** v1.0 — Production-Ready Script + Audio Generator

---

## Phase 1: Project Setup & Environment

**Goal:** Working Python environment with Kokoro TTS verified and project config aligned to decisions.

**Requirements covered:** SETUP-01, SETUP-02, SETUP-03

**Plans:** 2 plans

Plans:
- [ ] 01-01-PLAN.md — Config cleanup and test infrastructure
- [ ] 01-02-PLAN.md — Kokoro TTS verification, unit tests, and README

### Plans

**Plan 1.1 — Config Cleanup & Test Infrastructure**
- Update `config.py`: remove XTTS refs, add Kokoro voice ID, lang code, sample rate
- Update `requirements.txt`: replace TTS>=0.22.0 with kokoro>=0.9.4, soundfile, pytest
- Update `.env.example`: remove TTS_REF_WAV, add KOKORO_VOICE_ID
- Create `tests/conftest.py` for sys.path setup
- Update ROADMAP.md to reflect Kokoro and Claude Code decisions
- Delete stale `=0.9.4` directory artifact

**Plan 1.2 — Kokoro TTS Verification & Unit Tests**
- Create `test_tts.py` — Kokoro am_michael generates WAV audio, verify file output
- Create unit tests for src/ modules (course_loader, lesson_tracker, transcript_loader)
- Create `README.md` with setup instructions

**Plan 1.3 — Claude Code In-Session (no Python API file needed)**
- Script generation uses Claude Code in-session — no Python subprocess/API wrapper needed
- No test file required — Claude Code is the interface
- Document this decision in README.md

**Success criteria:**
- [ ] `python test_tts.py` produces a .wav file
- [ ] `pytest tests/ -v` passes all unit tests
- [ ] All dependencies installable via `pip install -r requirements.txt`

---

## Phase 2: Data Pipeline

**Goal:** All course content loaded and searchable; lesson index built with status tracking.

**Requirements covered:** DATA-01, DATA-02, DATA-03, DATA-04

### Plans

**Plan 2.1 — Transcript Indexer**
- `src/transcript_loader.py` — load `bootcamp_transcripts.json`, build keyword index
- `find_relevant_transcripts(lesson_keywords, max_results=5)` — score by keyword frequency
- Return: list of (score, filename, transcript_text) tuples
- Unit test: query "character consistency nano banana" → returns files 31, 32, 36

**Plan 2.2 — Course Content Loader**
- `src/course_loader.py` — parse `sources/sahinlabs_course.txt`
- Parse modules (M0-M5) and lessons into structured dict
- `get_lesson(module, lesson_num)` → returns lesson title + outline text
- Handle gracefully if file not yet present (show friendly message, pause)

**Plan 2.3 — Lesson Status Tracker**
- `src/lesson_tracker.py` — load/save `sources/lesson_status.json`
- Status per lesson: `pending` | `scripted` | `audio_done`
- Methods: `get_status(lesson_id)`, `set_status(lesson_id, status)`, `get_all()`
- Initialize from course loader — create entry for every lesson on first run

**Success criteria:**
- [ ] Transcript search returns relevant results for test queries
- [ ] Course content parses all 30+ lessons from .txt
- [ ] Status file persists between Python runs

---

## Phase 3: Script Generator

**Goal:** Interactive lesson selection → context assembly → Claude script generation → review → save.

**Requirements covered:** SCRPT-01 through SCRPT-06

### Plans

**Plan 3.1 — Context Assembler**
- `src/context_builder.py` — for a given lesson:
  - Get lesson outline from course loader
  - Extract lesson title keywords for transcript search
  - Fetch top-5 relevant bootcamp transcript segments
  - Return assembled context string (lesson outline + bootcamp excerpts)
- Include token count estimate in output

**Plan 3.2 — Claude Script Generator**
- `src/script_generator.py` — Claude API integration
- System prompt: tone (enthusiastic educator), AV script format definition, production marker guide, examples
- Use `anthropic.beta.prompt_caching` — cache system prompt + full bootcamp index
- Per-lesson call: inject lesson outline + assembled context
- Parse response into structured script object

**Plan 3.3 — Script Review CLI**
- `src/review_ui.py` — using `rich` for formatted terminal output
- Display generated script with syntax highlighting for production markers
- Options: (a)ccept / (e)dit in $EDITOR / (r)egenerate with note / (s)kip
- On accept: save to `scripts/M{module}L{lesson}_{slug}.md`
- Update lesson status to `scripted`

**Success criteria:**
- [ ] Running `python generate.py --lesson M1L1` generates a complete script
- [ ] Script saved as properly named .md file
- [ ] Script contains [SCREEN RECORDING] / [IMAGE] / [VIDEO] markers
- [ ] Script is 400-800 words (3-5 minute lesson)
- [ ] Lesson status updates to `scripted` after accept

---

## Phase 4: TTS Audio Generator

**Goal:** Convert any approved script to WAV audio via Kokoro TTS.

**Requirements covered:** TTS-01 through TTS-05

### Plans

**Plan 4.1 — Narration Extractor**
- `src/narration_extractor.py` — parse script .md file
- Extract only `[VO]` lines (strip all production markers)
- Join into clean narration text suitable for TTS
- Handle multi-paragraph scripts, preserve natural pause points

**Plan 4.2 — Kokoro Audio Generator**
- `src/audio_generator.py` — call Kokoro KPipeline with am_michael voice
- Handle long texts: split at sentence boundaries if > 2000 chars
- Concatenate audio chunks with numpy
- Save to `audio/M{module}L{lesson}_{slug}.wav`

**Plan 4.3 — Audio Quality Check**
- After generation: print duration, file size, path
- Optional playback prompt: (p)lay / (s)kip
- Update lesson status to `audio_done` on success

**Success criteria:**
- [ ] `python generate.py --audio M1L1` produces a .wav from existing script
- [ ] Audio duration matches estimated word count (±15%)
- [ ] Voice sounds natural and clear on 30s spot check

---

## Phase 5: Integrated Workflow & Polish

**Goal:** Single unified CLI with full lesson list, status view, and smooth end-to-end flow.

**Requirements covered:** WRK-01 through WRK-04

### Plans

**Plan 5.1 — Main CLI Menu**
- `generate.py` — main entry point using `rich` table display
- Startup: show all lessons with status (color-coded: pending/scripted/audio_done)
- Module headers grouping lessons
- Summary: "X pending scripts, Y awaiting audio, Z complete"

**Plan 5.2 — Unified Lesson Flow**
- `generate.py --lesson M1L1` — full flow: context → script → review → audio in one command
- `generate.py --list` — show lesson status table
- `generate.py --script-only M1L1` — generate script, skip audio
- `generate.py --audio-only M1L1` — generate audio from existing script
- `generate.py --dry-run M1L1` — show assembled context, token estimate, no API call

**Plan 5.3 — Error Handling & Resilience**
- Kokoro not loaded: clear error message with install instructions
- Claude API error: retry once, then show error with context saved to temp file
- Missing `sahinlabs_course.txt`: pause with setup instructions
- Partial audio generation failure: save progress, allow resume

**Success criteria:**
- [ ] `python generate.py` shows formatted lesson status table
- [ ] `python generate.py --lesson M0L1` completes end-to-end in < 2 minutes
- [ ] Error messages are actionable (tell you what to do)
- [ ] Dry-run works without any API calls

---

## Phase Sequence

```
Phase 1 (Setup)
    → Phase 2 (Data Pipeline)
        → Phase 3 (Script Gen)
            → Phase 4 (TTS Audio)
                → Phase 5 (Workflow)
```

Sequential — each phase builds on the previous. No parallel phases for this project.

---

## Definition of Done (v1.0)

- [ ] All 22 v1 requirements checked off
- [ ] At least 3 full lessons generated end-to-end (script + audio)
- [ ] Lesson status tracker persists correctly
- [ ] README accurate and complete
- [ ] `python generate.py --list` shows all 30+ lessons with status

---
*Roadmap created: 2026-03-26*
*Last updated: 2026-03-26 — Phase 1 plans created, Kokoro/Claude Code decisions applied*
