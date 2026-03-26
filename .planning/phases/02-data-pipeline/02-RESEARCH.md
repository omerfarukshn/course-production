# Phase 2: Data Pipeline - Research

**Researched:** 2026-03-26
**Domain:** Python data loading, JSON persistence, keyword search, course content parsing
**Confidence:** HIGH — all findings based on direct code inspection and live test execution

---

## Summary

Phase 2's three modules (`course_loader.py`, `lesson_tracker.py`, `transcript_loader.py`) were
built during Phase 1 as part of foundation work. Direct inspection and live test execution
confirm all 15 unit tests pass and the core functionality satisfies DATA-01 through DATA-04.

However, there are four specific gaps between the current implementations and what Phase 3
(Script Generator) will need, plus one test-quality issue the planner should close:

1. **Excerpt length is too short** — `transcript_loader` returns only the first 500 chars of a
   transcript (11.5% of average transcript). Phase 3's SCRPT-02 needs substantially more context
   per result to generate quality scripts.
2. **Score tiebreaking is non-deterministic** — 7 transcripts all score 4 for the canonical test
   query, so the roadmap's planned unit test ("returns files 31, 32, 36") cannot be asserted
   reliably without adding a secondary sort key (e.g., filename alphabetically or index number).
3. **M0L2 is absent** — The course file has no L2 in Module 0; the lesson list jumps M0L1 →
   M0L3. This is likely intentional content (the lesson was removed from the source). No code
   change needed, but the plan must document this and the test must not hard-code lesson count
   assumptions beyond what already passes.
4. **Lesson tracker tests mutate the real status file** — `test_set_status_valid` writes to
   `sources/lesson_status.json` and resets; there is no temp-file isolation. This works now, but
   is fragile if tests ever run in a different order or state.

**Primary recommendation:** Phase 2 plans should be verification-first — confirm each requirement
is fully met, close the excerpt-length gap (configurable excerpt size), add a tiebreak sort, and
add one isolated test for the tracker. No module needs a full rewrite.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DATA-01 | Load and index `bootcamp_transcripts.json` (98 files, keyword-scored search) | `transcript_loader.py` loads 98 files, keyword-scores, returns (score, fname, excerpt) tuples. **Gap:** excerpt is only 500 chars; needs configurable size for SCRPT-02. |
| DATA-02 | Load SahinLabs course content from `sources/sahinlabs_course.txt` | `course_loader.py` parses all 33 lessons from M0-M5, returns structured dicts. Fully satisfied. |
| DATA-03 | Build lesson index: M0-M5 × all sub-lessons, with status tracking per lesson | `lesson_tracker.init_if_needed()` creates 33 entries from course_loader. Fully satisfied including M3L5.5 (decimal ID). |
| DATA-04 | Save lesson status to disk (`sources/lesson_status.json`) — persists between sessions | `_save()` writes JSON, `_load_raw()` reads it. File confirmed on disk with 33 entries. Fully satisfied. |
</phase_requirements>

---

## Requirement-by-Requirement Gap Analysis

### DATA-01: transcript_loader.py

**What the requirement says:** Load and index `bootcamp_transcripts.json` (98 files,
keyword-scored search).

**What exists:**
- Loads from `BOOTCAMP_TRANSCRIPTS` path in config (hardcoded to `C:\Users\sahin\bootcamp_transcripts.json`)
- Module-level `_cache` variable caches the loaded JSON in memory across calls
- `_tokenize()` lowercases, extracts 3+ char words, filters 35 stopwords
- `find_relevant_transcripts(keywords, max_results=5)` returns `list[tuple[int, str, str]]`
- 4 unit tests pass — returns list, max_results respected, tuple structure, empty keywords

**Confirmed working:** 98 files load correctly. Query "character consistency DNA nano banana"
returns 5 results, all at score 4. Dataset confirmed: 98 keys, each with index, filename,
filesize_mb, duration_sec, transcript, word_count fields.

**Gaps:**

Gap 1 — Excerpt too short for Phase 3 context assembly.
- Current: `excerpt = transcript[:500].strip()`
- Average transcript is 4,353 chars; 500 chars is 11.5% of content
- 5 results × 500 chars = 2,500 chars of bootcamp context for script generation
- Phase 3 (SCRPT-02) requires "top-5 relevant bootcamp transcript segments" — the excerpt IS the
  segment. 500 chars (~100 words) is insufficient for a useful context segment in a script prompt.
- Recommended fix: make excerpt length configurable with a larger default (e.g., 1,500 chars).
  Add `excerpt_chars` parameter to `find_relevant_transcripts()`. No config.py change needed.

Gap 2 — Score tiebreaking is dict insertion order (non-deterministic for the test).
- The roadmap planned a specific unit test: "query 'character consistency nano banana' → returns
  files 31, 32, 36". Live run shows 7 files all score 4 for this query. With `max_results=5`,
  which 5 are returned depends on JSON file key order (insertion order in Python 3.7+ dict).
  File 37 and 36 appear at the top of the dict before 31 — so 36 is NOT in the top 5 results.
- The planned test assertion is wrong as written. Fix: add secondary sort by filename (or index
  field) so results are deterministic, then update the test to match actual sorted order, or
  assert "files 31, 32 appear in results" without asserting the exact 5.

Gap 3 — No test that the full text is searchable, only the first 500 chars (excerpt). The search
runs over the full `transcript` text, not the excerpt. This is correct. No gap here — confirmed
by inspection: `_tokenize(transcript)` uses the full text, excerpt is only the return value.

**DATA-01 verdict:** Mostly satisfied. Two improvements to make: configurable excerpt size,
deterministic sort. No structural change needed.

---

### DATA-02: course_loader.py

**What the requirement says:** Load SahinLabs course content from `sources/sahinlabs_course.txt`.

**What exists:**
- `load_course()` → nested dict `{module_num: {title, lessons: {lesson_num: {id, title, content}}}}`
- `get_lesson(module_num, lesson_num)` → lesson dict or None
- `list_all_lessons()` → flat list of all lessons with full fields
- `if not COURSE_FILE.exists()` → prints friendly Turkish error message and returns `{}`
- 6 unit tests pass — modules load, M0 exists, 33 lessons, required keys, get_lesson happy/sad path

**Confirmed working:** 33 lessons load across M0-M5. M0 has lessons 1, 3, 4, 5 (L2 absent in
source file — this is an intentional gap in the content, not a parser bug). M3L5.5 parses
correctly with the decimal lesson ID regex `r'^L(\d+(?:\.\d+)?):\s+(.+)'`. Lesson content
is non-empty for all 33 lessons. Sorting uses `float(x[0])` so decimal IDs sort correctly.

**No gaps.** DATA-02 is fully satisfied.

---

### DATA-03: lesson_tracker.py

**What the requirement says:** Build lesson index: M0-M5 × all sub-lessons, with status tracking
per lesson.

**What exists:**
- `init_if_needed()` — calls `list_all_lessons()`, creates entries for any lesson not already
  tracked, saves JSON. Idempotent on repeat calls.
- `get_status(lesson_id)` → str, defaults to "pending" for unknown IDs
- `set_status(lesson_id, status)` → validates against `{"pending", "scripted", "audio_done"}`,
  raises `ValueError` on invalid input
- `get_all()` → calls `init_if_needed()` then `_load_raw()`, returns full dict
- 5 unit tests pass

**Confirmed working:** Live run of `init_if_needed()` created 33 entries in lesson_status.json
including M3L5.5. All 33 are "pending". Status file confirmed on disk.

**Gap — Test isolation:** `test_set_status_valid` writes to the real `sources/lesson_status.json`.
It resets back to "pending" after the assertion, which means tests pass in isolation but mutation
of a shared file during a test run is fragile. If a test crashes mid-set, the file is left in
state "scripted" for M0L1. Fix: patch `LESSON_STATUS_FILE` in the test to use `tmp_path`.

**DATA-03 verdict:** Fully satisfied. One test hygiene improvement recommended.

---

### DATA-04: lesson_status.json persistence

**What the requirement says:** Save lesson status to disk — persists between sessions.

**What exists:**
- `_save(data)` writes JSON with indent=2 and ensure_ascii=False
- `_load_raw()` reads JSON if file exists, returns `{}` if not
- File is confirmed at `sources/lesson_status.json` with 33 entries

**No gaps.** DATA-04 is fully satisfied.

---

## Integration Concerns for Phase 3

Phase 3 (Script Generator) consumes the three Phase 2 modules. Two integration points to verify:

**Integration 1 — Context assembly (SCRPT-02):**
`context_builder.py` will call:
```python
lesson = get_lesson(module_num, lesson_num)          # → {id, title, content}
results = find_relevant_transcripts(keywords, 5)     # → [(score, fname, excerpt), ...]
```
The `lesson["content"]` field is the full lesson text (avg ~4,000 chars, confirmed 4,084 chars
for M1L1). That's solid for a system prompt context. But the `excerpt` at 500 chars is too
short. Phase 3 will need 1,000-2,000 chars per bootcamp segment to produce useful scripts.
This gap must be closed in Phase 2 so Phase 3 can consume it correctly.

**Integration 2 — Status updates (SCRPT-05, TTS-05):**
After script approval, Phase 3 will call `set_status(lesson_id, "scripted")`. After audio
generation, Phase 4 will call `set_status(lesson_id, "audio_done")`. Both flows work correctly
with the current `set_status` implementation. No changes needed here.

**Integration 3 — Lesson ID format:**
`course_loader` produces IDs like `"M1L1"`, `"M3L5.5"`. The tracker stores them by this key.
Phase 3's `generate.py --lesson M1L1` will need to split this string into module/lesson parts
to call `get_lesson("1", "1")`. This parsing belongs in Phase 3, not Phase 2. No gap in Phase 2.

**Integration 4 — Module ordering for display (WRK-01):**
`list_all_lessons()` sorts by `float(module_num)` and `float(lesson_num)` — this correctly
handles M3L5.5 appearing between M3L5 and M3L6. Phase 5's status table display will work.

---

## Architecture Patterns

### What Already Exists (Do Not Rebuild)

```
src/
├── course_loader.py      # load_course(), get_lesson(), list_all_lessons()
├── lesson_tracker.py     # init_if_needed(), get_status(), set_status(), get_all()
└── transcript_loader.py  # find_relevant_transcripts(keywords, max_results)

sources/
├── sahinlabs_course.txt   # 33 lessons, M0-M5, already parsing correctly
└── lesson_status.json     # 33 entries, all "pending", already on disk

config.py                  # COURSE_FILE, LESSON_STATUS_FILE, BOOTCAMP_TRANSCRIPTS paths
```

### Pattern: Thin module design

Each module does one thing, reads from config paths, no inter-module state except
`lesson_tracker` importing `course_loader` (correct dependency direction). Phase 3 will import
all three via `src.*` — no restructuring needed.

### Pattern: Config-driven paths

All file paths come from `config.py`. `BOOTCAMP_TRANSCRIPTS` is absolute (not project-relative),
which is correct since the bootcamp file lives outside the project directory.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| JSON persistence | Custom serializer | `json.dumps/loads` with `indent=2` (already in place) |
| Keyword search | TF-IDF library | Simple set intersection score (already in place, sufficient for 98 docs) |
| File path handling | `os.path.join` | `pathlib.Path` (already in place) |
| Status validation | Enum class | Simple set membership check (already in place) |

**Key insight:** With only 98 transcript files and simple keyword matching, a full-text search
library like Whoosh or Elasticsearch would be massive overkill. The current set-intersection
approach is correct and fast enough.

---

## Common Pitfalls

### Pitfall 1: Roadmap test assertion is wrong
**What goes wrong:** Plan 2.1 in ROADMAP says unit test should assert "query 'character
consistency nano banana' → returns files 31, 32, 36". Live test shows 7 files score 4 for
this query; file 36 does NOT appear in the top 5 results because dict iteration order places
files 19, 31, 32, 33, 35 first.
**How to avoid:** Either (a) add secondary sort by filename to make results deterministic, then
write the test against the actual sorted top 5, or (b) assert that score > 0 results are returned
and that result structure is correct (structure test already exists). Do not write a test that
asserts specific filenames without also fixing the sort.

### Pitfall 2: Test_set_status_valid mutates real status file
**What goes wrong:** If `test_set_status_valid` fails between `set_status("M0L1", "scripted")`
and the reset `set_status("M0L1", "pending")`, the lesson_status.json file on disk is left
in state "scripted". Subsequent test runs might have unexpected behavior.
**How to avoid:** Use `unittest.mock.patch` to redirect `LESSON_STATUS_FILE` to a `tmp_path`
tempfile for write tests.

### Pitfall 3: M0L2 absence surprises downstream code
**What goes wrong:** Phase 3's lesson selector may try to display "M0 — 5 lessons" but only
find 4. Or it might check for `get_lesson("0", "2")` and get None.
**How to avoid:** Document clearly that M0L2 is intentionally absent from the source file.
`get_lesson` already returns None gracefully. The tracker only creates entries for parsed
lessons, so M0L2 will never appear in lesson_status.json. No code fix needed — only
documentation.

### Pitfall 4: Excerpt-length assumption in Phase 3
**What goes wrong:** If Phase 3 is built assuming `excerpt` contains a full useful transcript
segment (1,000+ chars), it will silently produce scripts with very thin bootcamp context because
the current excerpt is only 500 chars.
**How to avoid:** Extend `find_relevant_transcripts` to accept `excerpt_chars=1500` parameter
before Phase 3 is built. This is a one-line change in transcript_loader.py.

---

## Code Examples

### Current transcript search (working, needs excerpt size fix)
```python
# Source: src/transcript_loader.py (live, tested)
def find_relevant_transcripts(keywords: list[str], max_results: int = 5) -> list[tuple]:
    # ... keyword scoring ...
    excerpt = transcript[:500].strip()   # <-- this line needs excerpt_chars parameter
    scored.append((score, fname, excerpt))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:max_results]
```

Recommended change (one line):
```python
def find_relevant_transcripts(
    keywords: list[str],
    max_results: int = 5,
    excerpt_chars: int = 1500,          # added
) -> list[tuple]:
    # ... keyword scoring ...
    excerpt = transcript[:excerpt_chars].strip()   # use parameter
    scored.append((score, fname, excerpt))
    # Add secondary sort for determinism:
    scored.sort(key=lambda x: (-x[0], x[1]))      # score desc, filename asc
    return scored[:max_results]
```

### Lesson tracker test isolation (what to fix)
```python
# Current (fragile — writes to real sources/lesson_status.json)
def test_set_status_valid():
    set_status("M0L1", "scripted")
    assert get_status("M0L1") == "scripted"
    set_status("M0L1", "pending")

# Recommended (isolated)
def test_set_status_valid(tmp_path):
    import src.lesson_tracker as lt
    from unittest.mock import patch
    fake_file = tmp_path / "lesson_status.json"
    with patch.object(lt, 'LESSON_STATUS_FILE', fake_file):
        lt.set_status("M0L1", "scripted")
        assert lt.get_status("M0L1") == "scripted"
```

### Integration pattern for Phase 3 context assembly
```python
# How Phase 3 will consume Phase 2 modules:
from src.course_loader import get_lesson
from src.transcript_loader import find_relevant_transcripts

lesson = get_lesson("1", "1")          # {id, title, content}
keywords = lesson["title"].lower().split()   # simple keyword extraction
segments = find_relevant_transcripts(keywords, max_results=5, excerpt_chars=1500)
# segments: [(score, fname, excerpt), ...]
```

---

## State of the Art

| Phase 1 Output | Phase 2 Status | What Phase 2 Actually Does |
|----------------|----------------|---------------------------|
| 3 modules created, 15 tests passing | Already built | Verify + close gaps |
| transcript excerpt = 500 chars | Gap | Extend to configurable (1500 recommended) |
| Score sort is score-only | Gap | Add secondary sort for determinism |
| Tracker tests mutate real file | Gap | Add tmp_path isolation |
| M0L2 absent | Documented | No code change needed |

---

## Open Questions

1. **Is M0L2 intentionally absent?**
   - What we know: Module 0 in `sahinlabs_course.txt` jumps L1 → L3. The parser is correct.
   - What's unclear: Was L2 ("The 48-Hour Challenge" per CLAUDE.md) intentionally omitted from
     the source file, or accidentally excluded?
   - Recommendation: Check the source file. If L2 should exist, add it. If omitted intentionally,
     document in a code comment in course_loader.py.

2. **What excerpt length is right for script generation quality?**
   - What we know: 500 chars is too short; average transcript is 4,353 chars.
   - What's unclear: At what excerpt length does Claude's script generation quality plateau?
   - Recommendation: Default to 1,500 chars (covers ~300 words, ~2.5 minutes of speech).
     Phase 3 testing will reveal if more is needed.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none (conftest.py handles sys.path only) |
| Quick run command | `python -m pytest tests/ -v` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DATA-01 | transcript_loader loads 98 files | unit | `python -m pytest tests/test_transcript_loader.py -v` | Yes |
| DATA-01 | keyword search returns scored tuples | unit | `python -m pytest tests/test_transcript_loader.py::test_find_relevant_result_tuple_structure -v` | Yes |
| DATA-01 | excerpt_chars parameter works | unit | `python -m pytest tests/test_transcript_loader.py::test_find_relevant_excerpt_chars -v` | No — Wave 0 gap |
| DATA-01 | score tiebreak is deterministic | unit | `python -m pytest tests/test_transcript_loader.py::test_find_relevant_deterministic -v` | No — Wave 0 gap |
| DATA-02 | course_loader returns 33 lessons | unit | `python -m pytest tests/test_course_loader.py -v` | Yes |
| DATA-02 | get_lesson returns correct content dict | unit | `python -m pytest tests/test_course_loader.py::test_get_lesson_returns_dict -v` | Yes |
| DATA-03 | init_if_needed creates 33 tracked lessons | unit | `python -m pytest tests/test_lesson_tracker.py::test_get_all_returns_dict -v` | Yes (partial) |
| DATA-03 | init_if_needed is idempotent | unit | `python -m pytest tests/test_lesson_tracker.py::test_init_idempotent -v` | No — Wave 0 gap |
| DATA-04 | lesson status persists to disk | unit | `python -m pytest tests/test_lesson_tracker.py::test_set_status_valid -v` | Yes (not isolated) |
| DATA-04 | status file survives process restart | integration | manual — run python, set status, restart python, check status | Manual only |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -v`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** All 15 existing + new tests green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_transcript_loader.py::test_find_relevant_excerpt_chars` — covers DATA-01 excerpt_chars parameter
- [ ] `tests/test_transcript_loader.py::test_find_relevant_deterministic` — covers DATA-01 sort determinism
- [ ] `tests/test_lesson_tracker.py::test_init_idempotent` — covers DATA-03 idempotent init
- [ ] Fix `tests/test_lesson_tracker.py::test_set_status_valid` to use tmp_path isolation

---

## Sources

### Primary (HIGH confidence)
- Direct code inspection: `src/course_loader.py`, `src/lesson_tracker.py`, `src/transcript_loader.py`
- Live test execution: `python -m pytest tests/ -v` — 15 passed in 0.25s confirmed
- Live module execution: all Python investigation scripts above run successfully

### Secondary (MEDIUM confidence)
- ROADMAP.md Plans 2.1-2.3 — planned test assertions (verified to be partially wrong re: file 36)
- Phase 1 SUMMARY files — confirm what was built and what passed

### Tertiary (LOW confidence)
- None — all findings are from direct code and data inspection

---

## Metadata

**Confidence breakdown:**
- Gap analysis: HIGH — directly measured from code + live test runs
- Excerpt length concern: HIGH — measured average transcript length (4,353 chars) and current limit (500)
- Tiebreak issue: HIGH — reproduced by running the exact query and seeing 7 files at score 4
- Test isolation issue: HIGH — read the test code, confirmed no patching

**Research date:** 2026-03-26
**Valid until:** 2026-06-26 (stable domain — Python stdlib + JSON, no external API changes expected)
