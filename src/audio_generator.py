"""
Audio generator — convert narration text to WAV via Kokoro KPipeline.

Lazy-loads the 82M model on first call. Chunks long text at sentence boundaries.
Writes WAV at 24000 Hz using soundfile.
"""
import re
import warnings
import numpy as np
import soundfile as sf
from pathlib import Path
from kokoro import KPipeline
from config import AUDIO_DIR, KOKORO_VOICE_ID, KOKORO_LANG_CODE, KOKORO_SAMPLE_RATE

_pipeline: KPipeline | None = None


def _get_pipeline() -> KPipeline:
    """Lazy singleton — loads Kokoro model once, reuses across calls."""
    global _pipeline
    if _pipeline is None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _pipeline = KPipeline(lang_code=KOKORO_LANG_CODE, repo_id='hexgrad/Kokoro-82M')
    return _pipeline


def chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    """Split text at sentence boundaries if exceeding max_chars.

    Uses regex lookbehind to split after sentence-ending punctuation (.!?).
    Each chunk contains complete sentences and is <= max_chars.
    """
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


def generate_audio(lesson_id: str, narration_text: str, slug: str) -> dict:
    """Generate WAV audio from narration text using Kokoro TTS.

    Args:
        lesson_id: e.g. "M0L1"
        narration_text: clean narration (no markers)
        slug: filename slug e.g. "welcome_what_makes_this_different"

    Returns:
        {"path": Path to .wav, "duration": float seconds}
    """
    pipeline = _get_pipeline()
    output_path = AUDIO_DIR / f"{lesson_id}_{slug}.wav"

    audio_chunks = []
    for chunk in chunk_text(narration_text):
        for result in pipeline(chunk, voice=KOKORO_VOICE_ID, speed=1.0):
            if result.audio is not None:
                audio_chunks.append(result.audio.numpy())

    audio = np.concatenate(audio_chunks)
    sf.write(str(output_path), audio, KOKORO_SAMPLE_RATE)

    duration = len(audio) / KOKORO_SAMPLE_RATE
    return {"path": output_path, "duration": duration}
