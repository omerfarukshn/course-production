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

# ElevenLabs TTS
ELEVENLABS_API_KEY    = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID   = "Cz0K1kOv9tD8l0b5Qu53"  # Jon
ELEVENLABS_MODEL_ID   = "eleven_turbo_v2_5"
ELEVENLABS_API_URL    = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

# Script generation
SCRIPT_MIN_WORDS = 300
SCRIPT_MAX_WORDS = 600
SCRIPT_STYLE = "enthusiastic educator, direct, conversational"

# Ensure dirs exist
for d in [SCRIPTS_DIR, AUDIO_DIR, SOURCES_DIR]:
    d.mkdir(parents=True, exist_ok=True)
