"""
Audio generator — convert narration text to MP3 via ElevenLabs REST API.
Jon voice (Cz0K1kOv9tD8l0b5Qu53), eleven_turbo_v2_5 model.
"""
import re
from pathlib import Path
import requests
from config import AUDIO_DIR, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL_ID, ELEVENLABS_API_URL


def text_cleaner(text: str) -> str:
    """Normalize text before TTS: expand abbreviations, strip extra whitespace."""
    # Expand common abbreviations
    text = re.sub(r'\be\.g\.\s*', 'for example ', text)
    text = re.sub(r'\bvs\.\s*', 'versus ', text)
    text = re.sub(r'\bw/\s*', 'with ', text)
    text = re.sub(r'\betc\.\s*', 'et cetera ', text)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n+', ' ', text)
    # Remove markdown artifacts
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+\s*', '', text)
    return text.strip()


def generate_audio(lesson_id: str, narration_text: str, slug: str) -> dict:
    """Generate MP3 audio from narration text using ElevenLabs Jon voice.

    Args:
        lesson_id: e.g. "M0L1"
        narration_text: clean narration (no markers)
        slug: filename slug e.g. "welcome_what_makes_this_different"

    Returns:
        {"path": Path to .mp3, "duration": float seconds}

    Raises:
        RuntimeError: if ElevenLabs API returns non-200
    """
    cleaned = text_cleaner(narration_text)
    output_path = AUDIO_DIR / f"{lesson_id}_{slug}.mp3"

    response = requests.post(
        ELEVENLABS_API_URL,
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "text": cleaned,
            "model_id": ELEVENLABS_MODEL_ID,
            "voice_settings": {
                "stability": 0.40,
                "similarity_boost": 0.88,
                "style": 0.15,
                "use_speaker_boost": True,
            },
            "output_format": "mp3_44100_128",
        },
        timeout=120,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"ElevenLabs API error ({response.status_code}): {response.text[:200]}. "
            f"Fix: check ELEVENLABS_API_KEY in .env"
        )

    output_path.write_bytes(response.content)

    # Estimate duration: ~150 wpm -> words / 150 * 60
    word_count = len(cleaned.split())
    duration = (word_count / 150) * 60

    return {"path": output_path, "duration": duration}
