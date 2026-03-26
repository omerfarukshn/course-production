# Requirements: SahinLabs Course Production System

**Defined:** 2026-03-26
**Core Value:** Every lesson must have a production-ready English script with [SCREEN]/[IMAGE]/[VIDEO] markers plus TTS audio — so Ömer can directly edit his videos without writing or recording anything from scratch.

## v1 Requirements

### Data Pipeline

- [x] **DATA-01**: Load and index `bootcamp_transcripts.json` (98 files, keyword-scored search)
- [x] **DATA-02**: Load SahinLabs course content from `sources/sahinlabs_course.txt`
- [x] **DATA-03**: Build lesson index: M0-M5 × all sub-lessons, with status tracking per lesson
- [x] **DATA-04**: Save lesson status to disk (`sources/lesson_status.json`) — persists between sessions

### Script Generation

- [x] **SCRPT-01**: Interactive lesson selector — browse lessons by module, see pending/done status
- [x] **SCRPT-02**: Context assembly — for selected lesson: pull lesson outline + top-5 relevant bootcamp transcript segments via keyword matching
- [x] **SCRPT-03**: Claude API call (Anthropic SDK) — generates English narration script with AV two-column format and [SCREEN RECORDING], [IMAGE: desc], [VIDEO: desc], [VO], [PAUSE] markers
- [x] **SCRPT-04**: Script review loop — display generated script in terminal, allow (a)ccept / (e)dit / (r)egenerate / (s)kip
- [x] **SCRPT-05**: Save approved script to `scripts/M{n}L{n}_{slug}.md`
- [x] **SCRPT-06**: Prompt caching — course content + bootcamp index cached across all 30 lesson generations (~$0.54 total cost)

### TTS Audio Generation

- [ ] **TTS-01**: Integrate with Chatterbox TTS Server via OpenAI-compatible REST API (`http://localhost:8004/v1/audio/speech`)
- [x] **TTS-02**: Extract [VO] narration lines from approved script (strip production markers)
- [ ] **TTS-03**: Generate .mp3 from narration text using selected male English voice
- [ ] **TTS-04**: Save audio to `audio/M{n}L{n}_{slug}.mp3`
- [ ] **TTS-05**: Mark lesson as `audio_done` in status tracker after successful generation

### Workflow & UX

- [ ] **WRK-01**: Main menu: list all lessons with status (pending / scripted / audio_done)
- [ ] **WRK-02**: Single-lesson mode: select → generate script → review → generate audio (all in one flow)
- [ ] **WRK-03**: Resume support — skip already-completed lessons, show progress summary on launch
- [ ] **WRK-04**: Dry-run flag (`--dry-run`) — show assembled context without calling API (for debugging)

### Project Setup

- [ ] **SETUP-01**: `requirements.txt` with pinned dependencies (anthropic, requests, rich for terminal UI)
- [ ] **SETUP-02**: `config.py` — configurable API key, Chatterbox URL, voice ID, output paths
- [ ] **SETUP-03**: `README.md` — setup instructions, how to run, how to add course content

## v2 Requirements

### Batch & Automation

- **BATCH-01**: Batch mode — generate all pending scripts in sequence with auto-approval
- **BATCH-02**: Batch TTS — convert all approved-but-no-audio scripts overnight
- **BATCH-03**: Cost estimator — show token/cost estimate before generating

### Quality

- **QUAL-01**: Script scoring — rate generated script on clarity, pacing, marker density
- **QUAL-02**: TTS voice comparison — generate same 30s excerpt in 3 voices, pick best
- **QUAL-03**: Word count / duration estimate per script (target: 3-5 min per lesson)

### Maggie Instagram Automation (separate project, tracked here for reference)

- **MAGGIE-01**: Post 3 photos/day at scheduled times to @itsmaggiexx via Instagram API
- **MAGGIE-02**: Music workaround — create Reels with embedded audio (music pre-mixed into video)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Turkish scripts | English only for this course version |
| Full batch automation (v1) | Ömer reviews each script — interactive is intentional |
| Video editing / assembly | Ömer handles this; tool produces script + audio only |
| Skool / platform upload | Local production tool; upload is manual |
| ChatGPT / OpenAI API | Using Claude API — better quality, already available |
| Multiple language TTS | English male voice only for this course |
| Web UI | Terminal/CLI only; simpler, faster to build |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SETUP-01 | Phase 1 | Pending |
| SETUP-02 | Phase 1 | Pending |
| SETUP-03 | Phase 1 | Pending |
| DATA-01 | Phase 2 | Complete |
| DATA-02 | Phase 2 | Complete |
| DATA-03 | Phase 2 | Complete |
| DATA-04 | Phase 2 | Complete |
| SCRPT-01 | Phase 3 | Complete |
| SCRPT-02 | Phase 3 | Complete |
| SCRPT-03 | Phase 3 | Complete |
| SCRPT-04 | Phase 3 | Complete |
| SCRPT-05 | Phase 3 | Complete |
| SCRPT-06 | Phase 3 | Complete |
| TTS-01 | Phase 4 | Pending |
| TTS-02 | Phase 4 | Complete |
| TTS-03 | Phase 4 | Pending |
| TTS-04 | Phase 4 | Pending |
| TTS-05 | Phase 4 | Pending |
| WRK-01 | Phase 5 | Pending |
| WRK-02 | Phase 5 | Pending |
| WRK-03 | Phase 5 | Pending |
| WRK-04 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-26*
*Last updated: 2026-03-26 after initial definition*
