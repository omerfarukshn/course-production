---
phase: 05-integrated-workflow-polish
plan: 02
subsystem: ui
tags: [rich, cli, lesson-tracker, status-table, generate]

# Dependency graph
requires:
  - phase: 04-tts-audio-generator
    provides: generate.py interactive workflow with --audio flag
  - phase: 02-data-pipeline
    provides: lesson_tracker.get_all() returning {lesson_id: {status, title}}
provides:
  - generate.py startup status table grouped by module with emoji status indicators
  - --list CLI flag to print status table and exit
  - show_status_table() function callable from main workflow
affects: [future-polish, any-plan-using-generate.py]

# Tech tracking
tech-stack:
  added: []
  patterns: [rich.table output with color-coded status, UTF-8 stdout reconfigure for Windows emoji compatibility]

key-files:
  created: []
  modified: [generate.py]

key-decisions:
  - "sys.stdout.reconfigure(encoding='utf-8') added at top of generate.py to handle emoji in Windows legacy terminals (cp1254)"
  - "show_status_table() called before interactive menu so Omer always sees status on startup without extra command"

patterns-established:
  - "STATUS_EMOJI dict maps status strings to emoji glyphs for consistent display across codebase"
  - "Module grouping by lesson_id[0:2] (e.g. 'M0', 'M1') from get_all() keys"

requirements-completed: [WRK-01, WRK-03]

# Metrics
duration: 5min
completed: 2026-03-27
---

# Phase 5 Plan 02: Startup Status Table Summary

**Rich status table added to generate.py showing all 33 lessons grouped by module with emoji (X/notebook/checkmark) on every startup and via --list flag**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-27T10:48:21Z
- **Completed:** 2026-03-27T10:52:37Z
- **Tasks:** 1/1
- **Files modified:** 1

## Accomplishments
- show_status_table() function prints all lessons grouped by M0-M5 with color-coded status rows
- --list flag added to argparse: prints table and exits cleanly (exit 0)
- Startup display: table shown before interactive menu + "Press Enter to continue" prompt
- Summary line: "N audio_done · M scripted · Z pending" counts at bottom of table
- UTF-8 reconfiguration fix so emoji render correctly in Windows terminals without env vars

## Task Commits

Each task was committed atomically:

1. **Task 1: Add show_status_table() and --list flag to generate.py** - `737efcf` (feat)

**Plan metadata:** (docs commit below)

## Files Created/Modified
- `generate.py` - Added show_status_table(), STATUS_EMOJI, --list argparse flag, UTF-8 stdout reconfigure, startup call before while loop

## Decisions Made
- Added `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at module top to handle Windows cp1254 encoding that blocks emoji rendering — avoids requiring users to set PYTHONIOENCODING manually
- Called show_status_table() before the interactive loop (not inside it) so the table appears once per session, not on every module return

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed UnicodeEncodeError for emoji in Windows legacy terminal**
- **Found during:** Task 1 (verification run)
- **Issue:** Windows cp1254 encoding can't encode ❌/📝/✅ characters — Rich raised UnicodeEncodeError in _windows_renderer.py
- **Fix:** Added `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at top of generate.py before any imports that use Console
- **Files modified:** generate.py
- **Verification:** `python generate.py --list` runs without error and shows emoji in output
- **Committed in:** 737efcf (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix for Windows Unicode)
**Impact on plan:** Required for the feature to work on Omer's Windows machine. No scope creep.

## Issues Encountered
None beyond the Unicode fix above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Status table feature complete; generate.py now shows live lesson progress on every launch
- 49 tests all pass (no regressions)
- Ready for remaining phase 05 plans (ElevenLabs TTS integration, etc.)

## Self-Check: PASSED

- FOUND: generate.py (modified with show_status_table, --list flag, UTF-8 fix)
- FOUND: .planning/phases/05-integrated-workflow-polish/05-02-SUMMARY.md
- FOUND: commit 737efcf (feat(05-02): add show_status_table() and --list flag to generate.py)

---
*Phase: 05-integrated-workflow-polish*
*Completed: 2026-03-27*
