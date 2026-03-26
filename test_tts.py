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
