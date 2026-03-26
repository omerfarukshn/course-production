"""
SahinLabs Course Production — Config
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base dirs
COURSE_DIR = Path(os.getenv("COURSE_DIR", r"C:\Users\sahin\projects\course-production"))
SCRIPTS_DIR = COURSE_DIR / "scripts"
AUDIO_DIR   = COURSE_DIR / "audio"
SOURCES_DIR = COURSE_DIR / "sources"

# Source files
COURSE_FILE          = SOURCES_DIR / "sahinlabs_course.txt"
LESSON_STATUS_FILE   = SOURCES_DIR / "lesson_status.json"
BOOTCAMP_TRANSCRIPTS = Path(os.getenv("BOOTCAMP_TRANSCRIPTS", r"C:\Users\sahin\bootcamp_transcripts.json"))

# Kokoro TTS
KOKORO_VOICE_ID    = os.getenv("KOKORO_VOICE_ID", "am_michael")
KOKORO_LANG_CODE   = "a"   # American English
KOKORO_SAMPLE_RATE = 24000

# Script generation
SCRIPT_MIN_WORDS = 300
SCRIPT_MAX_WORDS = 600
SCRIPT_STYLE = "enthusiastic educator, direct, conversational"

# Ensure dirs exist
for d in [SCRIPTS_DIR, AUDIO_DIR, SOURCES_DIR]:
    d.mkdir(parents=True, exist_ok=True)
