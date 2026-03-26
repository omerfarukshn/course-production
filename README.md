# SahinLabs Course Production

AI-assisted pipeline that turns a structured course outline into narrated, ready-to-publish lesson audio files.

## Stack

| Tool | Purpose |
|------|---------|
| Kokoro TTS (`am_michael`) | Narration generation |
| Claude (in-session via Claude Code) | Script writing |
| Python 3.11+ | Orchestration |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # edit if needed
```

## Verify TTS Works

```bash
python test_tts.py
```

Generates `audio/test_output.wav`. Should be ~4s, ~150 KB.

## Run Unit Tests

```bash
python -m pytest tests/ -v
```

## Produce a Lesson Script

```bash
python produce.py --lesson M1L1
```

## Project Structure

```
course-production/
├── config.py              # paths + Kokoro settings
├── produce.py             # main entry point
├── test_tts.py            # TTS smoke test
├── requirements.txt
├── src/
│   ├── course_loader.py   # parse sahinlabs_course.txt
│   ├── lesson_tracker.py  # track lesson status
│   └── transcript_loader.py  # find relevant bootcamp transcripts
├── tests/                 # unit tests (pytest)
├── sources/               # course outline + lesson_status.json
├── scripts/               # generated .txt scripts
└── audio/                 # generated .wav files
```
