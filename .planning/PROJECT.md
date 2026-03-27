# SahinLabs Course Production System

## What This Is

An interactive Python CLI for producing the SahinLabs AI Income Club course. It combines SahinLabs lesson outlines with AI Video Bootcamp transcripts to generate English narration scripts (with [SCREEN]/[IMAGE]/[VIDEO] production markers), then converts approved scripts to MP3 audio via ElevenLabs TTS. Built for Ömer — solo creator producing 33 video lessons across 6 modules (M0–M5).

## Core Value

Every lesson must have a production-ready English script with [SCREEN]/[IMAGE]/[VIDEO] markers plus TTS audio — so Ömer can directly edit his videos without writing or recording anything from scratch.

## Requirements

### Validated

- ✓ Parse and index `bootcamp_transcripts.json` (keyword-scored search) — v1.0
- ✓ Load SahinLabs course content from `sources/sahinlabs_course.txt` — v1.0
- ✓ Interactive lesson selector — module browser, lesson status display — v1.0
- ✓ Script generation via Claude API — English narration with [SCREEN RECORDING], [IMAGE], [VIDEO] markers — v1.0
- ✓ Script review loop — (a)ccept/(e)dit/(r)egenerate/(s)kip — v1.0
- ✓ ElevenLabs TTS audio generation — Jon voice, MP3 output — v1.0 *(adjusted from Chatterbox local)*
- ✓ Organized output: `scripts/M{n}L{n}_{title}.md` + `audio/M{n}L{n}_{title}.mp3` — v1.0
- ✓ Lesson status tracking — pending/scripted/audio_done, persists between sessions — v1.0
- ✓ Prompt caching — course content + bootcamp index cached (~$0.54 for all 33 lessons) — v1.0
- ✓ Single-command lesson production — `--lesson M0L1` full flow — v1.0
- ✓ Dry-run mode — `--dry-run M0L1` context inspection, zero API cost — v1.0
- ✓ Startup status table — grouped by module with `--list` flag — v1.0

### Active

*(No active requirements — v1.0 complete. Define v1.1 with `/gsd:new-milestone`)*

### Out of Scope

| Feature | Reason |
|---------|--------|
| Turkish scripts | English only for this course version |
| Full batch automation | Ömer reviews each script — interactive is intentional |
| Video editing / assembly | Ömer handles this; tool produces script + audio only |
| Skool / platform upload | Local production tool; upload is manual |
| ChatGPT / OpenAI API | Using Claude API — better quality, already available |
| Multiple language TTS | English male voice only for this course |
| Web UI | Terminal/CLI only; simpler, faster to build |
| Chatterbox local TTS | Replaced by ElevenLabs — no GPU required, better quality |

## Context

- **Shipped:** v1.0 on 2026-03-27 — 5 phases, 11 plans, 1,863 LOC Python, 49 tests
- **Course structure:** 6 modules (M0–M5), 33 lessons total
- **TTS:** ElevenLabs Jon voice (eleven_turbo_v2_5) via REST API — MP3 output
- **LLM:** Claude API (Anthropic SDK) with TextBlockParam prompt caching
- **Platform:** Windows 11, Python, `C:\Users\sahin\projects\course-production\`
- **Test suite:** 49 pytest tests, all mocked (no live API calls in tests)
- **CLI modes:** `--list`, `--lesson M0L1`, `--dry-run M0L1`, `--audio M0L1`, interactive

## Constraints

- **Budget:** ElevenLabs API key available; Kokoro removed (no GPU dependency)
- **Hardware:** Windows 11, RTX 3050 4GB (no longer needed for TTS)
- **Language:** English only — narration scripts must be natural, fluent English
- **Process:** Interactive one-lesson-at-a-time — not fully automated batch (Ömer reviews each script)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude API for script generation | Already in environment, no extra key, best quality | ✓ Works well — prompt caching saves ~80% tokens |
| ElevenLabs Jon voice (v1.0 switch) | No GPU required, cloud API, consistent quality | ✓ MP3 output, TTS-01 satisfied |
| Interactive workflow (not batch) | Ömer wants to review each script before audio | ✓ Override guard prevents accidental regeneration |
| Production markers in script | Guides video editing without additional documentation | ✓ All scripts use [SCREEN]/[IMAGE]/[VIDEO] |
| excerpt_chars=1500 | Phase 3 context_builder needs longer bootcamp excerpts | ✓ Better script context quality |
| Dry-run mode | Debug context without API cost | ✓ Essential for iteration |
| Startup status table | Ömer always sees progress without extra command | ✓ Grouped by module with emoji |
| parse_lesson_id() strict regex | Prevents silent misrouting to wrong lesson | ✓ Clear error on bad M0L1 format |
| Audio prompt defaults to 'n' | Prevents accidental ElevenLabs credit spend | ✓ User explicitly opts in to audio |

---
*Last updated: 2026-03-27 after v1.0 milestone*
