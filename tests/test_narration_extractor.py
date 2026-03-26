import pytest
from pathlib import Path
from unittest.mock import patch


def test_extract_strips_headings(tmp_path):
    script = tmp_path / "test.md"
    script.write_text("# Lesson 0.1: Title\n\nHello world.", encoding="utf-8")
    from src.narration_extractor import extract_narration
    result = extract_narration(script)
    assert "Lesson 0.1" not in result
    assert "Hello world." in result


def test_extract_strips_standalone_markers(tmp_path):
    script = tmp_path / "test.md"
    markers = "[PAUSE]\n[VO]\n[SCREEN RECORDING: desc]\n[IMAGE: photo]\n[VIDEO: clip]"
    script.write_text(f"Hello.\n{markers}\nGoodbye.", encoding="utf-8")
    from src.narration_extractor import extract_narration
    result = extract_narration(script)
    assert "[PAUSE]" not in result
    assert "[VO]" not in result
    assert "[SCREEN RECORDING" not in result
    assert "[IMAGE" not in result
    assert "[VIDEO" not in result
    assert "Hello." in result
    assert "Goodbye." in result


def test_extract_keeps_plain_text(tmp_path):
    script = tmp_path / "test.md"
    script.write_text("Welcome to the course.\n[PAUSE]\nLet's begin.", encoding="utf-8")
    from src.narration_extractor import extract_narration
    result = extract_narration(script)
    assert "Welcome to the course." in result
    assert "Let's begin." in result


def test_extract_joins_paragraphs(tmp_path):
    script = tmp_path / "test.md"
    script.write_text("First paragraph.\n\nSecond paragraph.", encoding="utf-8")
    from src.narration_extractor import extract_narration
    result = extract_narration(script)
    assert result == "First paragraph. Second paragraph."


def test_extract_empty_script(tmp_path):
    script = tmp_path / "test.md"
    script.write_text("", encoding="utf-8")
    from src.narration_extractor import extract_narration
    result = extract_narration(script)
    assert result == ""


def test_extract_title_only(tmp_path):
    script = tmp_path / "test.md"
    script.write_text("# Lesson 1.1: Some Title\n\n", encoding="utf-8")
    from src.narration_extractor import extract_narration
    result = extract_narration(script)
    assert result == ""


def test_find_script_path_found(tmp_path):
    (tmp_path / "M0L1_welcome.md").write_text("content", encoding="utf-8")
    with patch("src.narration_extractor.SCRIPTS_DIR", tmp_path):
        from src.narration_extractor import find_script_path
        result = find_script_path("M0L1")
        assert result is not None
        assert result.name == "M0L1_welcome.md"


def test_find_script_path_not_found(tmp_path):
    with patch("src.narration_extractor.SCRIPTS_DIR", tmp_path):
        from src.narration_extractor import find_script_path
        result = find_script_path("M9L9")
        assert result is None
