"""
Unit tests for audio_generator module.
Uses mocked KPipeline — no actual GPU or model load needed.
"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock


def _make_mock_pipeline():
    """Create a mock KPipeline that yields Result-like objects with .audio tensors."""
    mock_pipeline_instance = MagicMock()
    # Each call to pipeline(text, voice=..., speed=...) returns iterator of results
    mock_result = MagicMock()
    # Simulate a 1-second audio chunk at 24000 Hz
    mock_result.audio = MagicMock()
    mock_result.audio.numpy.return_value = np.zeros(24000, dtype=np.float32)
    mock_pipeline_instance.__call__ = MagicMock(return_value=iter([mock_result]))
    mock_pipeline_instance.return_value = iter([mock_result])
    # Make it callable
    mock_pipeline_instance.side_effect = lambda text, voice=None, speed=1.0: iter([mock_result])
    return mock_pipeline_instance


def test_chunk_text_short():
    from src.audio_generator import chunk_text
    result = chunk_text("Hello world.")
    assert result == ["Hello world."]


def test_chunk_text_long():
    from src.audio_generator import chunk_text
    # Build a string of ~3000 chars from repeated sentences
    sentences = ["This is sentence number {}.".format(i) for i in range(120)]
    text = " ".join(sentences)
    assert len(text) > 2000
    chunks = chunk_text(text, max_chars=2000)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= 2000


def test_chunk_text_preserves_sentences():
    from src.audio_generator import chunk_text
    result = chunk_text("First sentence. Second sentence. Third sentence.", max_chars=35)
    # Each chunk should contain complete sentences
    for chunk in result:
        # No chunk should end mid-word (no truncation)
        assert chunk.endswith(".") or chunk.endswith("!") or chunk.endswith("?") or chunk == ""


def test_generate_audio_creates_wav(tmp_path):
    mock_pipeline = _make_mock_pipeline()
    with patch("src.audio_generator._get_pipeline", return_value=mock_pipeline), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        result = generate_audio("M0L1", "Hello world.", "welcome")
        assert result["path"].exists()
        assert result["path"].suffix == ".wav"


def test_generate_audio_filename_pattern(tmp_path):
    mock_pipeline = _make_mock_pipeline()
    with patch("src.audio_generator._get_pipeline", return_value=mock_pipeline), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        result = generate_audio("M0L1", "Hello world.", "welcome")
        assert result["path"].name == "M0L1_welcome.wav"


def test_generate_audio_calls_pipeline_with_voice(tmp_path):
    mock_pipeline = _make_mock_pipeline()
    with patch("src.audio_generator._get_pipeline", return_value=mock_pipeline), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        generate_audio("M0L1", "Hello.", "welcome")
        # Verify pipeline was called with correct voice
        call_args = mock_pipeline.call_args
        assert call_args[1].get("voice") == "am_michael" or \
               (len(call_args[0]) > 1 and call_args[0][1] == "am_michael")


def test_generate_audio_chunks_long_text(tmp_path):
    mock_pipeline = _make_mock_pipeline()
    with patch("src.audio_generator._get_pipeline", return_value=mock_pipeline), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        long_text = " ".join(["Sentence number {}.".format(i) for i in range(150)])
        assert len(long_text) > 2000
        generate_audio("M0L1", long_text, "welcome")
        # Pipeline should be called more than once (once per chunk)
        assert mock_pipeline.call_count >= 2


def test_generate_audio_returns_path_and_duration(tmp_path):
    mock_pipeline = _make_mock_pipeline()
    with patch("src.audio_generator._get_pipeline", return_value=mock_pipeline), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        result = generate_audio("M0L1", "Hello world.", "welcome")
        assert isinstance(result["path"], Path)
        assert isinstance(result["duration"], float)
        assert result["duration"] > 0
