# SahinLabs Course Production System

## What This Is

An interactive Python-based production tool for the SahinLabs AI Income Club course. It combines SahinLabs lesson outlines with AI Video Bootcamp transcripts to generate high-quality English narration scripts (with production markers for screen/image/video cues), then converts approved scripts to TTS audio via Chatterbox local. Built for Ömer — solo creator producing 30+ video lessons.

## Core Value

Every lesson must have a production-ready English script with [SCREEN]/[IMAGE]/[VIDEO] markers plus TTS audio — so Ömer can directly edit his videos without writing or recording anything from scratch.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Parse and index `bootcamp_transcripts.json` to extract relevant sections per lesson
- [ ] Load SahinLabs course content from `sources/sahinlabs_course.txt`
- [ ] Interactive lesson selector — pick a lesson, see outline + bootcamp context, generate script
- [ ] Script generation via Claude API — English narration with [SCREEN RECORDING], [IMAGE: description], [VIDEO: description] production markers
- [ ] Script review loop — show generated script, allow edit/approve before saving
- [ ] TTS audio generation via Chatterbox local — high-quality male English voice
- [ ] Organized output: `scripts/M{n}L{n}_{title}.md` + `audio/M{n}L{n}_{title}.mp3`
- [ ] Lesson status tracking — mark lessons as pending/scripted/audio-done

### Out of Scope

- Automatic video editing or assembly — Ömer will edit manually using the scripts + audio
- Turkish language output — English only for this system
- Uploading to Skool or any platform — local production tool only
- Instagram/social media posting — separate Maggie project
- Custom GPT via ChatGPT UI — using Claude API instead (no extra key needed)

## Context

- **Data sources:** `C:\Users\sahin\bootcamp_transcripts.json` (AI Video Bootcamp transcripts, already exists) + `C:\Users\sahin\projects\course-production\sources\sahinlabs_course.txt` (Ömer will prepare)
- **Course structure:** 6 modules (M0–M5), ~30 lessons total (see CLAUDE.md for full outline)
- **Script format:** Professional English narration for screen recording + generative media. Production markers guide Ömer when to cut to screen capture, AI-generated image, or video clip. Ömer handles the editing.
- **TTS:** Chatterbox local (runs on RTX 3050 4GB VRAM). Previously used — 4 voice samples generated. Need to select best high-quality male English voice.
- **Platform:** Windows 11, Python, `C:\Users\sahin\projects\course-production\`
- **LLM:** Claude (Anthropic API or claude CLI) — best quality, already available in Claude Code environment

## Constraints

- **Budget:** $0 TTS — Chatterbox local only, no paid voice APIs
- **Hardware:** RTX 3050 4GB VRAM — Chatterbox must fit in GPU memory
- **Data:** Course content .txt must be provided by Ömer before script generation can begin
- **Language:** English only — narration scripts must be natural, fluent English
- **Process:** Interactive one-lesson-at-a-time — not fully automated batch (Ömer reviews each script)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude API for script generation | Already in environment, no extra key, best quality | — Pending |
| Chatterbox for TTS | Free, local, GPU-accelerated, previously tested | — Pending |
| Interactive workflow (not batch) | Ömer wants to review each script before audio generation | — Pending |
| Production markers in script | Guides video editing without additional documentation | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-26 after initialization*
