# Course Production System — Research Findings

*Generated: 2026-03-26*

---

## 1. Chatterbox TTS on Windows + GPU

### Hardware Compatibility (RTX 3050 4GB)
- Chatterbox Turbo requires ~4.5 GB VRAM — RTX 3050 4GB is **borderline**
- CPU fallback is supported if GPU memory is insufficient (no code changes needed)
- Consistently outperforms ElevenLabs in blind evaluations; MIT licensed

### Installation (Windows)
**Recommended:** Portable Windows GUI — `Chatterbox TTS Desktop` on itch.io (AmpedHorizon)
- Pre-packaged with all dependencies; click `start.bat` to run
- Includes web UI + OpenAI-compatible API endpoints
- No system Python installation required

**Alternative:** `Chatterbox-TTS-Server` GitHub — more control, same model

### Usage
- Supports voice cloning from seconds of reference audio (no training)
- Emotion control capable, multilingual
- Outputs .mp3 directly (no conversion needed)
- For programmatic use: OpenAI-compatible REST API (`/v1/audio/speech`)

### Decision
Start with portable GUI. If 4GB VRAM fails → CPU mode (slower but works).

---

## 2. Claude API for Script Generation

### Context Window
- Claude Sonnet supports 200K tokens; Claude 3.5/4 models support up to 1M tokens
- No long-context surcharge anymore (flat per-token pricing)
- Can load full bootcamp_transcripts.json + all course content + 30 lesson outlines in one prompt

### Cost Estimate (30 lessons)
| Approach | Cost |
|----------|------|
| Basic (no caching) | ~$1.80 total |
| With prompt caching (90% discount on cached input) | ~$0.54 total |

Using Claude Sonnet 4.6: $3/M input, $15/M output. Each script ~2000 tokens.

### Best Practice
- Cache system prompt + course outline + bootcamp transcripts (pay once)
- Per-lesson: only the lesson-specific block is uncached
- System prompt should include: tone, [SCREEN]/[IMAGE]/[VIDEO] marker format, example output
- Pacing guideline: ~150 words = 1 minute of audio

### Script Output Format
```
[0:00-0:10] VISUAL: [SCREEN RECORDING: Dashboard overview]
            AUDIO: [VO] "Let's start by..."

[0:10-0:35] VISUAL: [IMAGE: DNA Triangulation diagram]
            AUDIO: [VO] "The three-lock framework..."
```

---

## 3. bootcamp_transcripts.json Processing

### Actual Structure (from codebase inspection)
The file is a **dict of filename → transcript object**, not segmented:
```json
{
  "01_0427.m4a": {
    "index": 1,
    "filename": "01_0427.m4a",
    "filesize_mb": 7.9,
    "duration_sec": 342.0,
    "transcript": "Hi guys, in this video I want to..."
  },
  "31_Character Consistency with Nano Banana (NEW).m4a": { ... }
}
```

Total: **98 audio files** with full transcript text per file. Topics include:
- Nano Banana / Higgsfield tools (character consistency, image editing)
- Kling, Veo 3, Seedance video generation
- Meta ads (campaigns, audiences, budgets, creatives)
- AI influencers, UGC, monetization
- General AI video production

### Search Strategy
Keyword matching against full transcript text per file:
```python
def find_relevant_transcripts(lesson_keywords, max_results=5):
    scored = []
    for filename, entry in transcripts.items():
        text = entry['transcript'].lower()
        score = sum(kw.lower() in text for kw in lesson_keywords)
        if score > 0:
            scored.append((score, filename, entry))
    scored.sort(reverse=True)
    return scored[:max_results]
```

Most relevant files per SahinLabs module:
- **M0 (Foundations/Higgsfield):** files 01, 24, 25 (tool intro, Cdream, onboarding)
- **M1 (Character Consistency):** files 31, 33 (Nano Banana consistency, Seedance)
- **M2 (Video Production):** files 15, 37, 43 (Kling, Veo 3, Hailou)
- **M3 (Social Media):** files 02, 23 (UGC, community growth)
- **M4 (Monetization):** files 44, 16 (AI influencers, affiliate)
- **M5 (Scaling):** files 04, 14 (summary, Paul's ads course)

---

## 4. Production Marker Conventions

### Standard Format (AV Two-Column Script)
```
[0:00-0:10] VISUAL: [SCREEN RECORDING: SahinLabs dashboard]
            AUDIO: [VO] "Welcome to Module 1..."

[0:10-0:35] VISUAL: [IMAGE: DNA Triangulation grid — 3 reference angles]
            AUDIO: [VO] "The three-lock framework keeps your character..."

[0:35-1:00] VISUAL: [VIDEO: Character reveal across 5 consistent shots]
            AUDIO: [VO] "This is what 100% consistency looks like."
```

### Marker Vocabulary
| Marker | Use |
|--------|-----|
| `[SCREEN RECORDING: description]` | Live desktop/app walkthrough |
| `[IMAGE: description]` | Static visual — diagram, photo, generated image |
| `[VIDEO: description]` | Motion clip — generative video, B-roll |
| `[VO]` | Voiceover narration (TTS reads this) |
| `[TEXT OVERLAY: "text"]` | Title cards, on-screen text |
| `[PAUSE: Xs]` | Silent beat for emphasis |
| `[TRANSITION: fade/cut]` | Scene change |

### TTS-Specific Notes
- Target 130-150 WPM (comfortable listening pace)
- Use commas for natural breath points
- Avoid unexplained acronyms
- `[PAUSE: 2s]` for emphasis between sections
- Duration estimate: `words / 2.75 = seconds`

---

## Key Implementation Decisions

| Decision | Recommendation | Reason |
|----------|---------------|--------|
| TTS Tool | Chatterbox portable GUI | Free, local, best quality, CPU fallback |
| LLM | Claude Sonnet via Anthropic SDK | Best quality, prompt caching, ~$0.54 total |
| Transcript search | Keyword scoring against full text | Simple, no index overhead, 98 files is small |
| Script format | AV two-column with timestamps | Industry standard, guides editing |
| Session flow | Load all sources on startup, interactive per-lesson | Fast iteration, human review each step |
