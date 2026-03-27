# Phase 5: Integrated Workflow & Polish — Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** discuss-phase

<domain>
## Phase Boundary

Deliver a fully unified CLI for the course production system:
- `python generate.py` → startup status table → interactive lesson selector
- `python generate.py --lesson M0L1` → script → review → audio (single-command full flow)
- `python generate.py --list` → show lesson status table only
- `python generate.py --dry-run M0L1` → show assembled context, no API call
- Replace Kokoro TTS with ElevenLabs API (Jon voice)
- Actionable error messages for all failure modes

</domain>

<decisions>
## Implementation Decisions

### Startup Display (WRK-01, WRK-03)
- **On `python generate.py` (no args):** Show full lesson status table FIRST, then proceed to interactive module selector.
- **Table format:** Color + emoji per row:
  - `❌` pending (dim/gray)
  - `📝` scripted (yellow)
  - `✅` audio_done (green)
  - Module names as bold section headers (not separate rows)
- **Summary line** below table: "X pending scripts, Y awaiting audio, Z complete"
- After table, existing interactive module → lesson selector continues as-is

### --lesson Unified Flow (WRK-02)
- `python generate.py --lesson M0L1` runs: context assemble → script generate → review loop → **"Generate audio? (y/n)"** prompt → audio generation
- After script acceptance, always ask separately before audio: user can skip audio if they only want the script
- If lesson already `scripted` or `audio_done`: warn and offer override: "M0L1 is already scripted. Regenerate? (y/n)"
- If user says no to override: exit cleanly without changes

### ElevenLabs TTS Backend (replaces Kokoro)
- **Voice:** Jon, ID: `Cz0K1kOv9tD8l0b5Qu53`
- **API settings:**
  - `stability`: 0.40
  - `similarity_boost`: 0.88
  - `style`: 0.15
  - `use_speaker_boost`: true
- **Output format:** `mp3_44100_128` → save as `.mp3` (replaces `.wav`)
- **text_cleaner function:** strip extra whitespace, expand abbreviations before API call to prevent Jon from stumbling
- **Config:** `ELEVENLABS_API_KEY` from `.env`, `ELEVENLABS_VOICE_ID = "Cz0K1kOv9tD8l0b5Qu53"` in `config.py`
- Remove all Kokoro imports/config from `config.py` and `audio_generator.py`
- `audio_entrypoint.py` remains orchestrator — only the generation layer changes

### Error Handling (Plan 5.3)
- All error messages must be **actionable**: state what failed + exactly what to do
- Examples:
  - `❌ ElevenLabs API error (401): Invalid API key. Fix: check ELEVENLABS_API_KEY in .env`
  - `❌ Course file not found: sources/sahinlabs_course.txt. Fix: add the course content file and restart.`
  - `❌ Claude API error (rate limit). Retrying in 10s... (1/2)`
- Claude API: retry once automatically, then show error with context saved to `temp_context.txt`
- Missing `sahinlabs_course.txt`: pause with setup instructions, don't crash

### Dry-run (WRK-04)
- `python generate.py --dry-run M0L1` → assemble context, print outline + bootcamp excerpts, show token estimate — no Claude API call, no ElevenLabs call
- Token estimate: show approximate input token count based on assembled context

### --list Flag
- `python generate.py --list` → print the status table and exit (no interactive menu)

### Claude's Discretion
- Exact Rich table column widths and padding
- Token estimation formula (rough character count / 4)
- Retry delay duration for Claude API (suggest 10s)
- Internal text_cleaner implementation details (regex patterns)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core source files
- `generate.py` — Current entrypoint (argparse, interactive flow, --audio flag already wired)
- `src/audio_generator.py` — Kokoro implementation to replace with ElevenLabs
- `src/audio_entrypoint.py` — Orchestrator that calls audio_generator (keep interface, swap backend)
- `src/lesson_tracker.py` — get_all(), get_status(), set_status() — use for startup table
- `src/review_ui.py` — show_module_menu(), show_lesson_menu() — reuse in unified flow
- `src/context_builder.py` — assemble_context() — reuse in --lesson flow
- `src/script_generator.py` — generate_script() — reuse in --lesson flow
- `config.py` — Remove Kokoro config, add ElevenLabs config

### Planning docs
- `.planning/REQUIREMENTS.md` — WRK-01 through WRK-04 must all be covered
- `.planning/STATE.md` — Current decisions and progress

</canonical_refs>

<specifics>
## Specific Ideas

### ElevenLabs Jon — exact API call structure
```python
response = requests.post(
    "https://api.elevenlabs.io/v1/text-to-speech/Cz0K1kOv9tD8l0b5Qu53",
    headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
    json={
        "text": cleaned_text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.40,
            "similarity_boost": 0.88,
            "style": 0.15,
            "use_speaker_boost": True
        },
        "output_format": "mp3_44100_128"
    }
)
```

### text_cleaner
- Strip multiple spaces/newlines to single
- Expand: "e.g." → "for example", "vs." → "versus", "w/" → "with"
- Remove markdown formatting artifacts if any remain

### Startup table sketch
```
  SahinLabs Course Production

  MODULE 0: Foundations
  ❌  M0L1  Welcome & What Makes This Different
  ✅  M0L2  The 48-Hour Challenge
  ...

  MODULE 1: Consistent Character Creation
  ❌  M1L1  The Character Bible
  ...

  📊 Status: 1 audio_done · 0 scripted · 32 pending

  [press enter to continue]
```

</specifics>

<deferred>
## Deferred Ideas

- Batch mode (generate all pending scripts overnight) — v2 requirement BATCH-01
- Voice comparison (generate same excerpt in 3 voices, pick best) — v2 QUAL-02
- Word count / duration estimate per script — v2 QUAL-03
- Kokoro as fallback when ElevenLabs offline — can be added later if needed

</deferred>

---

*Phase: 05-integrated-workflow-polish*
*Context gathered: 2026-03-27 via discuss-phase*
