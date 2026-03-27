"""
Unit tests for audio_generator module.
Uses mocked requests.post — no actual API call, no GPU needed.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def _make_mock_response(status_code=200, content=b"fake_mp3_bytes"):
    """Create a mock requests.Response-like object."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.content = content
    mock_resp.text = "Invalid API key" if status_code != 200 else ""
    return mock_resp


def test_text_cleaner_strips_extra_whitespace():
    from src.audio_generator import text_cleaner
    result = text_cleaner("hello   world\n\nfoo")
    assert result == "hello world foo"


def test_text_cleaner_expands_abbreviations():
    from src.audio_generator import text_cleaner
    assert text_cleaner("e.g. this") == "for example this"
    assert text_cleaner("vs. that") == "versus that"
    assert text_cleaner("w/ something") == "with something"


def test_generate_audio_creates_mp3(tmp_path):
    with patch("src.audio_generator.requests.post", return_value=_make_mock_response()), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        result = generate_audio("M0L1", "Hello world.", "welcome")
        assert result["path"].exists()
        assert result["path"].suffix == ".mp3"


def test_generate_audio_filename_pattern(tmp_path):
    with patch("src.audio_generator.requests.post", return_value=_make_mock_response()), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        result = generate_audio("M0L1", "Hello world.", "welcome")
        assert result["path"].name == "M0L1_welcome.mp3"


def test_generate_audio_calls_elevenlabs_endpoint(tmp_path):
    mock_post = MagicMock(return_value=_make_mock_response())
    with patch("src.audio_generator.requests.post", mock_post), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        generate_audio("M0L1", "Hello.", "welcome")
        call_args = mock_post.call_args
        url = call_args[0][0]
        assert "Cz0K1kOv9tD8l0b5Qu53" in url


def test_generate_audio_sends_correct_voice_settings(tmp_path):
    mock_post = MagicMock(return_value=_make_mock_response())
    with patch("src.audio_generator.requests.post", mock_post), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        generate_audio("M0L1", "Hello.", "welcome")
        call_kwargs = mock_post.call_args[1]
        voice_settings = call_kwargs["json"]["voice_settings"]
        assert voice_settings["stability"] == 0.40
        assert voice_settings["similarity_boost"] == 0.88
        assert voice_settings["style"] == 0.15
        assert voice_settings["use_speaker_boost"] is True


def test_generate_audio_returns_path_and_duration(tmp_path):
    with patch("src.audio_generator.requests.post", return_value=_make_mock_response()), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        result = generate_audio("M0L1", "Hello world.", "welcome")
        assert isinstance(result["path"], Path)
        assert isinstance(result["duration"], float)
        assert result["duration"] > 0


def test_generate_audio_raises_on_api_error(tmp_path):
    with patch("src.audio_generator.requests.post", return_value=_make_mock_response(status_code=401)), \
         patch("src.audio_generator.AUDIO_DIR", tmp_path):
        from src.audio_generator import generate_audio
        with pytest.raises(RuntimeError, match="ElevenLabs API error \\(401\\)"):
            generate_audio("M0L1", "Hello.", "welcome")
