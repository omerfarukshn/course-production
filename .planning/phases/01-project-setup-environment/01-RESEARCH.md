# Phase 1: Project Setup & Environment - Research

**Researched:** 2026-03-26
**Domain:** Python project configuration, Kokoro TTS integration, test infrastructure
**Confidence:** HIGH

---

## Summary

Phase 1 is primarily a "clean up what exists and verify it works" phase, not a greenfield setup. The
project already has a working Python environment with Kokoro 0.9.4 installed, three functional src/
modules (course_loader, lesson_tracker, transcript_loader), and a basic config.py and requirements.txt.
The only real work is: (1) update config.py to reflect the Kokoro decision instead of XTTS, (2) update
requirements.txt to match reality, (3) write test_tts.py that proves Kokoro am_michael generates audio
from this project's venv, (4) write unit tests for the three existing src/ modules, and (5) update
ROADMAP.md to reflect the real decisions made.

The most important thing to understand is that **config.py currently references XTTS** (TTS_MODEL,
TTS_LANGUAGE, TTS_REF_WAV pointing to a bootcamp wav) even though Kokoro am_michael is the decided
TTS. This mismatch must be corrected before any later phases build on config.py. Similarly,
requirements.txt has `TTS>=0.22.0` (the Coqui library for XTTS) which should be replaced with
`kokoro>=0.9.4` and `soundfile`.

**Primary recommendation:** Update config.py + requirements.txt first, then write test_tts.py and
unit tests — in that order. The entire phase should take one focused session.

---

<user_constraints>
## User Constraints (from HANDOFF.json / .continue-here.md)

### Locked Decisions
- TTS: **Kokoro v0.9.4, voice am_michael** — already installed and approved
- Script generation: **Claude Code in-session** — no Python subprocess / API calls in the codebase
- XTTS-v2 rejected (voice cloning quality + background noise issues)
- F5-TTS rejected (VRAM crash on batch)
- MOSS-TTS rejected (needs 8GB VRAM, system has 4GB)
- Voice cloning rejected (legal risk + quality issues)
- Voice sample location: `C:\Users\sahin\voice_samples\kokoro\am_michael_LONG.wav` (tested, approved)

### Claude's Discretion
- How to structure test_tts.py (what assertions to make, file output location)
- Whether to add pytest or use simple assert-based tests
- How to write unit tests for the three src/ modules (what edge cases to cover)
- Whether to add type annotations to test files

### Deferred Ideas (OUT OF SCOPE)
- Batch mode, cost estimator, script scoring — Phase 3/4/5
- Any changes to src/ module logic (only tests, not rewrites)
- Web UI, Skool integration, upload automation
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SETUP-01 | `requirements.txt` with pinned dependencies | Verified: existing file has wrong TTS lib; kokoro and soundfile already installed |
| SETUP-02 | `config.py` — configurable voice ID, output paths | Verified: current config.py has XTTS refs that must be replaced |
| SETUP-03 | `README.md` — setup instructions | Not yet created; straightforward doc task |
</phase_requirements>

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| kokoro | 0.9.4 | TTS generation (am_michael voice) | Already installed, tested, approved by Ömer |
| soundfile | 0.13.1 | Write numpy audio arrays to WAV/MP3 | Already installed; Kokoro outputs numpy float32 tensors |
| rich | >=13.0 | Terminal UI (tables, colors) | Already in requirements.txt, needed by Phase 5 |
| python-dotenv | >=1.0 | Load .env vars into config.py | Already in requirements.txt |
| torch | 2.6 | Required by Kokoro internally | Already installed with CUDA 12.4 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydub | >=0.25 | Audio concat / WAV-to-MP3 conversion | Phase 4, when stitching audio chunks |
| pytest | latest | Unit test runner | test_tts.py and src/ module tests |
| numpy | (with torch) | Audio array handling | Already present as torch dependency |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| soundfile | scipy.io.wavfile | soundfile simpler API, already installed |
| pytest | plain assert scripts | pytest gives better diffs and -x flag, minimal overhead |

**Installation (what's missing from current requirements.txt):**
```bash
pip install kokoro>=0.9.4 soundfile
# Remove: TTS>=0.22.0 (Coqui — heavy, wrong library)
```

**Version verification (already done):**
- kokoro: 0.9.4 (confirmed via `python -c "import kokoro; print(kokoro.__version__)"`)
- soundfile: 0.13.1 (confirmed via `pip show soundfile`)
- TTS>=0.22.0 in requirements.txt is stale — Coqui library for XTTS, not needed

---

## Architecture Patterns

### Recommended Project Structure (current + what Phase 1 adds)
```
course-production/
├── config.py              # UPDATE: remove XTTS refs, add Kokoro paths
├── requirements.txt       # UPDATE: kokoro>=0.9.4 soundfile, remove TTS>=0.22.0
├── .env.example           # UPDATE: add KOKORO_VOICE_ID, KOKORO_VOICE_WAV
├── README.md              # CREATE: setup instructions
├── test_tts.py            # CREATE: proves Kokoro am_michael works
├── tests/                 # CREATE: unit tests for src/ modules
│   ├── test_course_loader.py
│   ├── test_lesson_tracker.py
│   └── test_transcript_loader.py
├── src/
│   ├── course_loader.py   # EXISTS: 33 lessons parse correctly — no changes
│   ├── lesson_tracker.py  # EXISTS: status JSON works — no changes
│   └── transcript_loader.py  # EXISTS: keyword search works — no changes
├── scripts/               # EXISTS: empty output folder
├── audio/                 # EXISTS: empty output folder
└── sources/               # EXISTS: sahinlabs_course.txt + lesson_status.json
```

### Pattern 1: Kokoro TTS Generation
**What:** Initialize KPipeline once, call it as a generator, collect audio chunks, write WAV with soundfile.
**When to use:** test_tts.py and later audio_generator.py (Phase 4)

```python
# Source: verified from kokoro 0.9.4 source inspection
from kokoro import KPipeline
import soundfile as sf
import numpy as np

pipeline = KPipeline(lang_code='a')  # 'a' = American English

# Generator — yields Result objects per sentence/segment
chunks = []
for result in pipeline(text, voice='am_michael', speed=1.0):
    if result.audio is not None:
        chunks.append(result.audio.numpy())

# Concatenate and save
audio = np.concatenate(chunks)
sf.write('output.wav', audio, 24000)  # Kokoro sample rate = 24000 Hz
```

**Key API facts (verified from source):**
- `KPipeline(lang_code='a')` — 'a' is American English (not 'en')
- `pipeline(text, voice='am_michael', speed=1.0)` — returns a generator
- `result.audio` — torch.FloatTensor or None
- `result.audio.numpy()` — convert to numpy for soundfile
- Sample rate: **24000 Hz** (confirmed in source: "pred_dur frames to sample_rate 24000")
- Voice must be passed as string — `voice='am_michael'` (no .wav path needed; pack loaded internally)

### Pattern 2: config.py Kokoro Section (replacement for XTTS section)
```python
# Current (WRONG — XTTS):
TTS_REF_WAV  = Path(os.getenv("TTS_REF_WAV", r"C:\Users\sahin\voice_samples\ref_bootcamp.wav"))
TTS_MODEL    = "tts_models/multilingual/multi-dataset/xtts_v2"
TTS_LANGUAGE = "en"

# Replacement (Kokoro):
KOKORO_VOICE_ID  = os.getenv("KOKORO_VOICE_ID", "am_michael")
KOKORO_LANG_CODE = "a"   # American English
KOKORO_SAMPLE_RATE = 24000
```

### Pattern 3: Unit Test Structure for src/ Modules
**What:** Minimal pytest tests that verify the three src/ modules work without mocking.
**When to use:** tests/test_*.py — run against real data files.

```python
# tests/test_course_loader.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.course_loader import load_course, list_all_lessons, get_lesson

def test_load_course_returns_modules():
    course = load_course()
    assert len(course) >= 6  # M0 through M5

def test_list_all_lessons_count():
    lessons = list_all_lessons()
    assert len(lessons) == 33  # verified: 33 lessons in the file

def test_get_lesson_returns_dict():
    lesson = get_lesson("1", "1")
    assert lesson is not None
    assert "id" in lesson
    assert lesson["id"] == "M1L1"
```

### Anti-Patterns to Avoid
- **Keeping TTS>=0.22.0 in requirements.txt:** This is the Coqui library (hundreds of MB), not Kokoro. Will confuse future maintainers and pip installs.
- **Using `voice='am_michael.wav'` with file path:** Kokoro voice IDs are short strings, not paths. The .wav files in `voice_samples/kokoro/` are for listening — Kokoro downloads its own voice tensors from HuggingFace.
- **Using `lang_code='en'`:** The correct code for American English is `'a'`. Using `'en'` will fail or use wrong phonemizer.
- **Writing test audio to `audio/`:** test_tts.py should write to a temp file or `audio/test_output.wav`, clearly named as a test artifact.
- **Importing config from a subdirectory without sys.path fix:** The three src/ modules use `from config import ...` which requires the project root on sys.path. Tests must add the project root.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| WAV file writing | Custom byte writer | `soundfile.write()` | Handles sample rate, channels, encoding correctly |
| Audio array concat | Manual numpy loops | `np.concatenate(chunks)` | Already in numpy, one line |
| Env var loading | Manual `os.environ.get` everywhere | `python-dotenv` + `config.py` | Already done — config.py pattern is correct |
| Test discovery | Custom test runner | `pytest` | Auto-discovery, better output, `-x` flag |

---

## Common Pitfalls

### Pitfall 1: XTTS vs Kokoro config mismatch
**What goes wrong:** Later phases (Phase 4 audio generator) import config.py and find `TTS_MODEL = "tts_models/..."` which causes confusion — devs try to load XTTS which isn't installed.
**Why it happens:** config.py was written before the TTS decision was finalized.
**How to avoid:** Update config.py in the first task of Phase 1. Remove ALL XTTS keys.
**Warning signs:** config.py still has `TTS_MODEL` or `TTS_LANGUAGE` keys.

### Pitfall 2: Voice ID confusion (WAV path vs voice name)
**What goes wrong:** test_tts.py passes `voice='C:/Users/sahin/voice_samples/kokoro/am_michael.wav'` — this is NOT how Kokoro works. Kokoro voice IDs are short strings like `'am_michael'`.
**Why it happens:** The `.wav` files in `voice_samples/kokoro/` were generated for listening comparison, not for use as Kokoro voice inputs.
**How to avoid:** Use `voice='am_michael'` as a string. Kokoro resolves this internally via its HuggingFace pack.
**Warning signs:** FileNotFoundError or unexpected voice behavior when path is passed as voice.

### Pitfall 3: sys.path not set for tests
**What goes wrong:** `pytest tests/test_course_loader.py` fails with `ModuleNotFoundError: No module named 'config'`.
**Why it happens:** The src/ modules do `from config import ...` which requires the project root on sys.path. pytest doesn't add it automatically.
**How to avoid:** Add `sys.path.insert(0, project_root)` at top of each test file, OR add `conftest.py` with `sys.path` setup.
**Warning signs:** ImportError on `config` when running tests from any directory other than project root.

### Pitfall 4: KPipeline generator not iterated
**What goes wrong:** `audio = pipeline(text, voice='am_michael')` — assigning the generator to a variable produces nothing. Must iterate.
**Why it happens:** KPipeline.__call__ returns a Generator, not audio directly.
**How to avoid:** Always use `for result in pipeline(...)` pattern.
**Warning signs:** `audio` variable is a generator object, not a tensor.

### Pitfall 5: requirements.txt `=0.9.4` directory artifact
**What goes wrong:** There is a directory named `=0.9.4` in the project root — likely from a botched `pip install kokoro==0.9.4` run without proper quoting on Windows.
**Why it happens:** Windows shell treated `kokoro==0.9.4` as a directory creation in some invocations.
**How to avoid:** The directory is harmless but should be deleted. Does not affect Python imports.
**Warning signs:** `ls` of project root shows `=0.9.4` as a folder entry.

---

## Code Examples

### Complete test_tts.py Pattern
```python
# Source: verified against kokoro 0.9.4 source inspection
"""
test_tts.py — verify Kokoro am_michael can generate audio from this project.
Run: python test_tts.py
Success: prints file path + duration, produces audio/test_output.wav
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro import KPipeline
from config import AUDIO_DIR, KOKORO_VOICE_ID, KOKORO_LANG_CODE, KOKORO_SAMPLE_RATE

TEST_TEXT = (
    "Welcome to SahinLabs AI Income Club. "
    "In this course, you'll learn to build consistent AI characters "
    "and turn them into a real income stream."
)
OUTPUT_FILE = AUDIO_DIR / "test_output.wav"


def main():
    print(f"Initializing Kokoro pipeline (lang_code='{KOKORO_LANG_CODE}')...")
    pipeline = KPipeline(lang_code=KOKORO_LANG_CODE)

    print(f"Generating audio for voice '{KOKORO_VOICE_ID}'...")
    chunks = []
    for result in pipeline(TEST_TEXT, voice=KOKORO_VOICE_ID, speed=1.0):
        if result.audio is not None:
            chunks.append(result.audio.numpy())

    assert chunks, "No audio chunks generated — pipeline returned empty results"

    audio = np.concatenate(chunks)
    sf.write(str(OUTPUT_FILE), audio, KOKORO_SAMPLE_RATE)

    duration = len(audio) / KOKORO_SAMPLE_RATE
    size_kb = OUTPUT_FILE.stat().st_size // 1024
    print(f"\nSUCCESS")
    print(f"  File:     {OUTPUT_FILE}")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Size:     {size_kb} KB")
    assert duration > 1.0, f"Audio too short: {duration:.1f}s"
    assert OUTPUT_FILE.exists()


if __name__ == "__main__":
    main()
```

### conftest.py for Tests
```python
# tests/conftest.py — ensures project root is on sys.path for all tests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

## State of the Art

| Old Approach (in current files) | Correct Approach | Impact |
|--------------------------------|------------------|--------|
| `TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"` | `KOKORO_VOICE_ID = "am_michael"` | Avoids importing Coqui TTS entirely |
| `TTS_REF_WAV` pointing to bootcamp audio | Not needed — Kokoro uses internal packs | Removes dependency on ref audio for TTS |
| `TTS>=0.22.0` in requirements.txt | `kokoro>=0.9.4 soundfile` | ~500MB lighter install |
| No test files | test_tts.py + tests/ directory | Phase gate: proves TTS works before Phase 4 |
| ROADMAP Plans 1.2/1.3 (Chatterbox, Claude API) | Kokoro + Claude Code in-session | Docs match reality |

**Deprecated/outdated in this project:**
- `TTS_MODEL`, `TTS_LANGUAGE`, `TTS_REF_WAV` keys in config.py — remove entirely
- `TTS>=0.22.0` in requirements.txt — replace with `kokoro>=0.9.4`
- ROADMAP Plan 1.2 title "Chatterbox TTS Setup" — update to "Kokoro TTS Verification"
- ROADMAP Plan 1.3 title "Claude API Connection Test" — update to "Claude Code In-Session (no test file needed)"
- `=0.9.4` directory in project root — artifact, delete it

---

## Open Questions

1. **Should test_tts.py output WAV or MP3?**
   - What we know: soundfile writes WAV natively; MP3 needs pydub + ffmpeg
   - What's unclear: pydub is already in requirements.txt but ffmpeg may not be in PATH
   - Recommendation: Write WAV for test_tts.py (simpler, no ffmpeg dependency); Phase 4 handles MP3 conversion

2. **Should ROADMAP.md Plan 1.3 be removed or updated?**
   - What we know: there's no Claude API in this project — scripts are generated by Claude Code in-session
   - What's unclear: does Ömer want a test file anyway, or just a note?
   - Recommendation: Update Plan 1.3 to document the in-session pattern instead of creating a test file; no Python test makes sense for in-session generation

3. **Is the `=0.9.4` directory harmless?**
   - What we know: it's an artifact from a Windows shell pip command, doesn't affect Python
   - Recommendation: Delete it as part of Phase 1 cleanup (one-liner)

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (not yet installed — see Wave 0) |
| Config file | none — conftest.py in tests/ for sys.path |
| Quick run command | `python test_tts.py` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SETUP-01 | requirements.txt has kokoro, soundfile, not TTS | manual check | `pip install -r requirements.txt` | ❌ Wave 0: update file |
| SETUP-02 | config.py loads Kokoro voice ID correctly | smoke | `python test_tts.py` | ❌ Wave 0: create test_tts.py |
| SETUP-03 | README.md exists with setup instructions | manual | n/a | ❌ Wave 0: create README.md |
| (implicit) | course_loader loads 33 lessons | unit | `pytest tests/test_course_loader.py -x` | ❌ Wave 0: create test |
| (implicit) | lesson_tracker persists status | unit | `pytest tests/test_lesson_tracker.py -x` | ❌ Wave 0: create test |
| (implicit) | transcript_loader returns results | unit | `pytest tests/test_transcript_loader.py -x` | ❌ Wave 0: create test |

### Sampling Rate
- **Per task commit:** `python test_tts.py` (proves TTS chain works)
- **Per wave merge:** `pytest tests/ -v` (all unit tests green)
- **Phase gate:** Both test_tts.py and pytest tests/ pass before Phase 2

### Wave 0 Gaps
- [ ] `tests/conftest.py` — sys.path setup for all test files
- [ ] `tests/test_course_loader.py` — covers 33-lesson parse, get_lesson, list_all
- [ ] `tests/test_lesson_tracker.py` — covers init, get_status, set_status, get_all
- [ ] `tests/test_transcript_loader.py` — covers keyword search returns results
- [ ] `test_tts.py` — Kokoro am_michael audio generation smoke test
- [ ] pytest install: `pip install pytest` — not in current requirements.txt

---

## Sources

### Primary (HIGH confidence)
- Kokoro 0.9.4 source code (live inspection via `inspect.getsource`) — KPipeline API, sample rate, voice string format, Result.audio property
- `python -c "import kokoro; print(kokoro.__version__)"` — version confirmed 0.9.4
- `pip show soundfile` — version 0.13.1 confirmed installed
- Live functional test: `from src.course_loader import list_all_lessons; print(len(list_all_lessons()))` → 33 ✓
- `.continue-here.md` — all locked decisions, Kokoro am_michael approval
- `.planning/HANDOFF.json` — machine-readable decision record

### Secondary (MEDIUM confidence)
- `requirements.txt` analysis — TTS>=0.22.0 is Coqui, not Kokoro (verified by library name difference)
- `config.py` analysis — XTTS refs confirmed, need replacement (direct file read)

### Tertiary (LOW confidence)
- None — all claims verified directly from source code or file inspection

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified installed + version confirmed
- Architecture: HIGH — Kokoro API verified from source inspection, patterns tested
- Pitfalls: HIGH — identified from direct code examination of existing files

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (Kokoro 0.9.4 is pinned; stable)
