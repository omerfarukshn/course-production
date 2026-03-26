# Phase 4: TTS Audio Generator - Research

**Researched:** 2026-03-27
**Domain:** Kokoro TTS (kokoro-onnx / kokoro Python package), audio file I/O, script parsing
**Confidence:** HIGH — all key findings verified by live execution against the installed environment

---

## Summary

Phase 4 converts approved script `.md` files to `.wav` audio using the locally-installed Kokoro
TTS library (`kokoro==0.9.4`). The library is already tested and working (`test_tts.py` passes,
`audio/test_output.wav` produced). The exact API — `KPipeline(lang_code='a')` called as a
generator yielding `Result` objects with `.audio` torch tensors — is confirmed by live
inspection. `soundfile` is already in `requirements.txt` and handles WAV writes correctly.

The script format is known from the one existing script (`M0L1_*.md`): narration text lives as
plain paragraphs mixed with standalone production-marker lines (`[PAUSE]`, `[VO]`,
`[SCREEN RECORDING: ...]`, `[IMAGE: ...]`, `[VIDEO: ...]`). All marker lines must be stripped;
everything else is narration. A 400-word script produces roughly 2474 chars — above the 2000-char
split threshold in the plan — so the chunking logic will be exercised immediately.

**Primary recommendation:** Build `narration_extractor.py` → `audio_generator.py` → wire into
`generate.py --audio` flag. Use `soundfile.write()` for WAV output at 24000 Hz. Split on
sentence boundaries via `re.split(r'(?<=[.!?])\s+', text)` when the full narration exceeds
2000 chars.

**Critical clarification:** `REQUIREMENTS.md` TTS-01 says "Chatterbox TTS Server via REST API"
but `STATE.md` explicitly records the decision: "TTS kararı: Kokoro `am_michael`". The project
has been running Kokoro since Phase 1. TTS-01 language is stale — implement with Kokoro, not
Chatterbox.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| TTS-01 | Integrate Kokoro TTS (locally installed) | KPipeline API confirmed; test_tts.py is working reference |
| TTS-02 | Extract [VO] narration lines from approved script | Script structure analyzed; regex strip pattern identified |
| TTS-03 | Generate .wav from narration text using am_michael | Full generation loop confirmed via test_tts.py |
| TTS-04 | Save audio to `audio/M{n}L{n}_{slug}.mp3` (plan says .wav) | AUDIO_DIR defined in config.py; soundfile.write confirmed |
| TTS-05 | Mark lesson as `audio_done` after successful generation | `set_status(lesson_id, 'audio_done')` already in lesson_tracker.py |
</phase_requirements>

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| kokoro | 0.9.4 (installed) | Text-to-speech synthesis | Already installed, tested, working with am_michael |
| soundfile | 0.13.1 (installed) | Write numpy arrays to WAV | Already in requirements.txt; WAV output verified |
| numpy | (installed with torch) | Concatenate audio chunks | Standard for array ops; already used in test_tts.py |
| torch | (installed with CUDA) | Kokoro's internal tensor type | KPipeline returns torch.Tensor; .numpy() needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| re (stdlib) | — | Strip markers, split sentences | Narration extractor regex patterns |
| pathlib (stdlib) | — | File path handling | Consistent with rest of codebase |
| rich (installed) | >=13.0 | Terminal output for quality check | Already used everywhere in project |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| soundfile | scipy.io.wavfile | soundfile already in requirements, handles float32 natively |
| soundfile | pydub | pydub in requirements.txt but unnecessary for simple WAV write |
| sentence boundary split | fixed 2000-char split | Sentence boundary preserves natural speech rhythm |

**Installation:** All dependencies already installed. No new packages needed.

**Version verification (live):**
- `kokoro==0.9.4` — confirmed `python -c "import kokoro; print(kokoro.__version__)"`
- `soundfile==0.13.1` — confirmed `python -c "import soundfile as sf; print(sf.__version__)"`

---

## Architecture Patterns

### Recommended Project Structure
```
src/
├── narration_extractor.py   # Parse .md → clean narration string
├── audio_generator.py       # Kokoro pipeline → WAV file
└── [existing modules]
audio/
└── M{n}L{n}_{slug}.wav      # Generated audio files
```

### Pattern 1: Kokoro KPipeline — Generator API
**What:** `KPipeline.__call__` is a generator that yields `Result` objects. Each Result has
`.audio` (torch.Tensor, shape `[N]`, float32) or `None`. Collect non-None chunks, concatenate,
write once.

**When to use:** Always — this is the only public API.

**Exact signature (verified by introspection):**
```python
# KPipeline.__init__
KPipeline(lang_code, repo_id=None, model=True, trf=False, en_callable=None, device=None)

# KPipeline.__call__
pipeline(text, voice=None, speed=1, split_pattern='\\n+', model=None)
```

**Example (from working test_tts.py):**
```python
# Source: C:/Users/sahin/projects/course-production/test_tts.py (verified working)
import numpy as np
import soundfile as sf
from kokoro import KPipeline
from config import AUDIO_DIR, KOKORO_VOICE_ID, KOKORO_LANG_CODE, KOKORO_SAMPLE_RATE

pipeline = KPipeline(lang_code=KOKORO_LANG_CODE)  # lang_code='a' for American English

chunks = []
for result in pipeline(text, voice=KOKORO_VOICE_ID, speed=1.0):
    if result.audio is not None:
        chunks.append(result.audio.numpy())  # torch.Tensor -> np.ndarray (float32)

audio = np.concatenate(chunks)
sf.write(str(output_path), audio, KOKORO_SAMPLE_RATE)  # 24000 Hz
```

**Warnings to expect (benign, suppress with logging or ignore):**
- `dropout option adds dropout after all but last recurrent layer` — PyTorch internal warning
- `torch.nn.utils.weight_norm deprecated` — FutureWarning from Kokoro's model
- `Defaulting repo_id to hexgrad/Kokoro-82M` — suppress by passing `repo_id='hexgrad/Kokoro-82M'`

**GPU behavior:** Kokoro auto-detects CUDA. On this machine (RTX 3050, CUDA available),
`pipeline.model` parameters land on `cuda:0`. The `device` parameter can override this.
82M model easily fits in 4GB VRAM.

### Pattern 2: Narration Extraction
**What:** Strip all production-marker lines from script `.md`, keep plain text paragraphs.

**Script structure (verified from M0L1_welcome_what_makes_this_different.md):**
```
# Lesson X.Y: Title          ← strip (starts with #)
                              ← blank lines: skip
Plain narration paragraph.    ← KEEP
[PAUSE]                       ← strip (standalone marker)
[VO]                          ← strip (standalone marker)
[SCREEN RECORDING: desc]      ← strip (production marker)
[IMAGE: desc]                 ← strip (production marker)
[VIDEO: desc]                 ← strip (production marker)
```

**Key insight from live analysis:** `[VO]` appears as a standalone line marker, NOT as a prefix
before narration text. All plain text paragraphs (not starting with `#` or `[`) are narration.
The "[VO] lines" mentioned in the plan description means: narration text that appears after
a `[VO]` marker, but in practice ALL non-marker, non-title text is narration. The extractor
should keep all plain text, not filter to only lines after `[VO]`.

**Extraction pattern:**
```python
import re

def extract_narration(script_path: Path) -> str:
    content = script_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    narration = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#'):          # Title/heading
            continue
        if re.match(r'^\[.+\]$', stripped):  # Standalone marker [PAUSE], [VO], [SCREEN...], etc.
            continue
        narration.append(stripped)
    return ' '.join(narration)
```

**Char count of M0L1 (402 words):** 2474 chars — already exceeds 2000-char threshold.
Chunking will be needed immediately on the first real script.

### Pattern 3: Long-Text Chunking
**What:** Kokoro handles long text internally via `split_pattern` (default `'\\n+'`), but
sending very long text in one call can cause quality degradation. The plan calls for explicit
splitting at sentence boundaries if > 2000 chars.

**Recommended approach — let Kokoro split:** The `split_pattern='\\n+'` default already splits
on paragraph boundaries. Since the narration extractor joins all text with spaces, the newlines
are lost. Two options:

**Option A (simpler):** Pass joined text directly — Kokoro's internal sentence splitter handles
it. This is what `test_tts.py` already does (no chunking needed for short tests).

**Option B (explicit chunking at sentence boundaries):**
```python
import re

def chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ''
    for sent in sentences:
        if len(current) + len(sent) + 1 <= max_chars:
            current = (current + ' ' + sent).strip()
        else:
            if current:
                chunks.append(current)
            current = sent
    if current:
        chunks.append(current)
    return chunks
```

**Recommendation:** Use Option B. Join chunks' audio arrays with `np.concatenate`. This matches
the plan spec and gives fine-grained control over generation quality.

### Pattern 4: WAV File Saving
```python
# soundfile handles float32 numpy arrays directly
# Output: 16-bit PCM WAV at 24000 Hz (verified format)
sf.write(str(output_path), audio_array, KOKORO_SAMPLE_RATE)
```

File naming convention (from config.py and ROADMAP.md):
```python
# audio/M{module}L{lesson}_{slug}.wav
# Example: audio/M0L1_welcome_what_makes_this_different.wav
# Slug comes from context_builder.make_slug() (already implemented)
```

### Pattern 5: Entrypoint Integration
**What:** Add `--audio` flag to existing `generate.py`.

**Current generate.py:** No CLI args — just `python generate.py` starts interactive mode.
Phase 5 plan defines full `--audio-only`, `--lesson`, etc. flags. Phase 4 adds `--audio M1L1`.

**Minimal implementation for Phase 4:**
```python
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio', metavar='LESSON_ID',
                        help='Generate audio for a lesson with existing script (e.g. M1L1)')
    args, _ = parser.parse_known_args()

    if args.audio:
        run_audio_generation(args.audio)
        return
    # ... existing interactive flow unchanged
```

**Lesson ID to script path lookup:** Use `context_builder.make_slug()` + lesson title, or
scan `scripts/` directory for files matching `M{m}L{l}_*.md`. The simpler approach is to
glob `SCRIPTS_DIR / f"M{m}L{l}_*.md"` and take the first match.

### Anti-Patterns to Avoid

- **Re-initializing KPipeline per call:** KPipeline loads the 82M model on init. Initialize
  once and reuse. Loading time is ~2-3 seconds on this hardware.
- **Using pydub for WAV output:** pydub requires ffmpeg for many formats. soundfile is already
  installed and handles float32 WAV directly — no subprocess dependency.
- **Importing torch directly in audio_generator.py:** Not needed. Use `result.audio.numpy()`
  — torch is an indirect dependency via kokoro.
- **Passing raw script markdown to KPipeline:** Always extract narration first. Marker text
  like "[SCREEN RECORDING: ...]" will be spoken aloud by the TTS.
- **Opening KPipeline with `device='cuda'`:** Let Kokoro auto-detect. RTX 3050 with 4GB VRAM
  handles Kokoro-82M comfortably with default settings.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Text-to-speech synthesis | Custom TTS | kokoro KPipeline | Already installed, tested, working |
| WAV file writing | struct.pack() | soundfile.write() | Float32 array → PCM WAV in one call |
| Audio concatenation | Custom array merge | np.concatenate() | Standard, already in test_tts.py |
| Sentence detection | Custom regex | re.split(r'(?<=[.!?])\s+', text) | Lookbehind handles boundaries correctly |

**Key insight:** `test_tts.py` is the authoritative reference for the entire audio generation
pipeline. It already demonstrates the exact pattern that `audio_generator.py` should follow.

---

## Common Pitfalls

### Pitfall 1: "[VO] lines only" misinterpretation
**What goes wrong:** If the extractor only keeps lines immediately following `[VO]` markers,
most narration is dropped. In the actual script, `[VO]` is a standalone separator line — all
surrounding plain text is narration regardless of position.
**Why it happens:** The ROADMAP.md description "Extract only [VO] lines" is ambiguous.
**How to avoid:** Keep ALL plain text that is not a heading and not a `[...]` marker line.
**Warning signs:** Extracted text is very short; audio duration is much less than expected.

### Pitfall 2: Lesson ID to script path mismatch
**What goes wrong:** `--audio M1L1` needs to find `scripts/M1L1_some_title.md` but the slug
is unknown at command-line time.
**Why it happens:** Script filenames include the slug from `make_slug()`.
**How to avoid:** Use `list(SCRIPTS_DIR.glob(f'M{m}L{l}_*.md'))` — glob by module/lesson
prefix, take first match, fail clearly if none found.
**Warning signs:** FileNotFoundError with full path shown.

### Pitfall 3: Status guard skipped
**What goes wrong:** Calling `--audio M1L1` on a lesson without a script (status=pending)
raises FileNotFoundError or produces empty audio.
**Why it happens:** No guard between lesson status check and audio generation.
**How to avoid:** Check `get_status(lesson_id) == 'scripted'` before attempting audio. Print
clear error if not scripted yet.

### Pitfall 4: Kokoro init warning spam
**What goes wrong:** Terminal output is cluttered with PyTorch warnings during KPipeline init.
**How to avoid:** Suppress with `warnings.filterwarnings('ignore')` or print "Loading TTS
model..." before init to signal expected delay.

### Pitfall 5: Audio duration validation math
**What goes wrong:** Duration check uses word count at 150 wpm but TTS speed is configurable.
**How to avoid:** Use actual audio length: `duration = len(audio) / KOKORO_SAMPLE_RATE`.
For ±15% check: `expected_seconds = word_count / 2.5` (150 wpm ÷ 60).

---

## Code Examples

### Minimal audio_generator.py structure
```python
# Source: derived from test_tts.py (C:/Users/sahin/projects/course-production/test_tts.py)
import numpy as np
import soundfile as sf
from pathlib import Path
from kokoro import KPipeline
from config import AUDIO_DIR, KOKORO_VOICE_ID, KOKORO_LANG_CODE, KOKORO_SAMPLE_RATE

_pipeline: KPipeline | None = None

def _get_pipeline() -> KPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = KPipeline(lang_code=KOKORO_LANG_CODE)
    return _pipeline

def generate_audio(lesson_id: str, narration_text: str, slug: str) -> Path:
    pipeline = _get_pipeline()
    module, lesson = _parse_lesson_id(lesson_id)  # "M1L2" -> (1, 2)
    output_path = AUDIO_DIR / f"M{module}L{lesson}_{slug}.wav"

    chunks = []
    for chunk_text in _split_text(narration_text):
        for result in pipeline(chunk_text, voice=KOKORO_VOICE_ID, speed=1.0):
            if result.audio is not None:
                chunks.append(result.audio.numpy())

    audio = np.concatenate(chunks)
    sf.write(str(output_path), audio, KOKORO_SAMPLE_RATE)
    return output_path
```

### narration_extractor.py core function
```python
# Source: derived from script analysis (live verification of M0L1 script structure)
import re
from pathlib import Path

def extract_narration(script_path: Path) -> str:
    """Extract plain narration text from a script .md file.

    Strips: headings (#), standalone markers ([PAUSE], [VO], [SCREEN RECORDING:...], etc.)
    Keeps: all other non-empty lines joined with spaces.
    """
    content = script_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    narration = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            continue
        if re.match(r'^\[.+\]$', stripped):
            continue
        narration.append(stripped)
    return ' '.join(narration)
```

### Script path lookup from lesson ID
```python
from config import SCRIPTS_DIR

def find_script_path(lesson_id: str) -> Path | None:
    """Find script file for a lesson ID like 'M1L2'."""
    # lesson_id format: M{module}L{lesson}, e.g. M0L1, M3L2
    matches = list(SCRIPTS_DIR.glob(f"{lesson_id}_*.md"))
    return matches[0] if matches else None
```

### Quality check after generation
```python
duration = len(audio) / KOKORO_SAMPLE_RATE
size_kb = output_path.stat().st_size // 1024
word_count = len(narration_text.split())
expected_seconds = word_count / 2.5  # 150 wpm
ratio = duration / expected_seconds
within_bounds = 0.85 <= ratio <= 1.15

console.print(f"Duration:  {duration:.1f}s (expected {expected_seconds:.0f}s, ratio {ratio:.2f})")
console.print(f"File size: {size_kb} KB")
console.print(f"Path:      {output_path}")
if not within_bounds:
    console.print("[yellow]Warning: duration outside ±15% of word-count estimate[/yellow]")
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| XTTS / TTS>=0.22.0 | kokoro>=0.9.4 | Phase 1 decision | Lighter, no GPU required for small models |
| Chatterbox REST API (TTS-01 spec) | Kokoro local Python | Phase 1 decision (STATE.md) | No server process needed, $0 cost |

**Deprecated/outdated:**
- Chatterbox TTS Server: REQUIREMENTS.md TTS-01 references this but STATE.md records the
  final decision as Kokoro. Ignore the REST API spec entirely.
- `TTS>=0.22.0`: removed from requirements.txt in Phase 1, replaced with `kokoro>=0.9.4`.

---

## Open Questions

1. **MP3 vs WAV output format**
   - What we know: REQUIREMENTS.md TTS-03/04 say `.mp3`; ROADMAP.md Phase 4 says `.wav`;
     config.py has `KOKORO_SAMPLE_RATE = 24000` (WAV-compatible); soundfile writes WAV natively
   - What's unclear: Which format is actually wanted?
   - Recommendation: Use `.wav` — it matches ROADMAP.md (the authoritative plan doc),
     soundfile produces it natively, and REQUIREMENTS.md likely wasn't updated after
     the Kokoro decision. Add `AUDIO_FORMAT = 'wav'` to config.py for future flexibility.

2. **Pipeline reuse across multiple lessons in batch**
   - What we know: KPipeline takes ~2s to initialize; lazy singleton pattern works
   - What's unclear: Whether the pipeline accumulates state between calls
   - Recommendation: Use module-level lazy singleton (`_pipeline = None`); safe per Kokoro's
     stateless generation API.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none (pytest discovers tests/ automatically) |
| Quick run command | `pytest tests/test_narration_extractor.py tests/test_audio_generator.py -x` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TTS-01 | KPipeline generates audio from text | integration | `python test_tts.py` | ✅ (test_tts.py) |
| TTS-02 | extract_narration strips all markers, keeps plain text | unit | `pytest tests/test_narration_extractor.py -x` | ❌ Wave 0 |
| TTS-02 | extract_narration handles empty/title-only scripts | unit | `pytest tests/test_narration_extractor.py -x` | ❌ Wave 0 |
| TTS-03 | generate_audio produces WAV file | integration | `pytest tests/test_audio_generator.py -x` | ❌ Wave 0 |
| TTS-04 | WAV path matches `audio/M{m}L{l}_{slug}.wav` pattern | unit | `pytest tests/test_audio_generator.py -x` | ❌ Wave 0 |
| TTS-05 | status updated to `audio_done` after generation | unit | `pytest tests/test_audio_generator.py -x` | ❌ Wave 0 |

**Note on TTS-03 integration test:** Calling KPipeline in unit tests is slow (~5s) and requires
GPU. Recommended pattern: mock the pipeline in unit tests, test real generation only in
`test_tts.py` which is run manually. Use `unittest.mock.patch` on `audio_generator._get_pipeline`.

### Sampling Rate
- **Per task commit:** `pytest tests/test_narration_extractor.py tests/test_audio_generator.py -x`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_narration_extractor.py` — covers TTS-02 (marker stripping, plain text extraction)
- [ ] `tests/test_audio_generator.py` — covers TTS-03, TTS-04, TTS-05 (mocked pipeline)

*(Existing test infrastructure: conftest.py with sys.path, 33 tests green, pytest 9.0.2)*

---

## Sources

### Primary (HIGH confidence)
- `test_tts.py` (project file, verified working) — complete KPipeline usage pattern
- Live Python introspection (`inspect.signature`) — KPipeline.__init__ and __call__ exact signatures
- Live execution (`python -c`) — Result object attributes, audio tensor shape, device behavior
- `config.py` (project file) — KOKORO_VOICE_ID, KOKORO_LANG_CODE, KOKORO_SAMPLE_RATE, AUDIO_DIR
- `scripts/M0L1_welcome_what_makes_this_different.md` (project file) — actual script structure
- `.planning/STATE.md` (project file) — Kokoro decision and rationale

### Secondary (MEDIUM confidence)
- `requirements.txt` (project file) — confirmed kokoro>=0.9.4, soundfile, pydub present
- `generate.py` (project file) — existing entrypoint structure for --audio integration

### Tertiary (LOW confidence)
- None — all findings verified by live execution

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified by `import` and `__version__` checks
- Architecture: HIGH — KPipeline API verified by introspection + live generation test
- Script parsing: HIGH — actual script file analyzed with live Python
- Pitfalls: HIGH — derived from actual code structure analysis, not speculation

**Research date:** 2026-03-27
**Valid until:** 2026-06-27 (kokoro 0.9.4 is stable; API unlikely to change in 90 days)
