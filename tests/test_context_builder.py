# tests/test_context_builder.py — Unit tests for context_builder module (SCRPT-02, SCRPT-05)
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_extract_keywords_returns_list():
    from src.context_builder import extract_keywords
    result = extract_keywords("Character Bible", "Build consistent characters")
    assert isinstance(result, list)
    assert len(result) > 0
    assert len(result) <= 10
    for kw in result:
        assert isinstance(kw, str)


def test_make_slug_basic():
    from src.context_builder import make_slug
    assert make_slug("Character Bible") == "character_bible"
    assert make_slug("M0L3 \u2014 Tool Setup") == "m0l3_tool_setup"


def test_assemble_context_structure():
    with patch("src.context_builder.get_lesson") as mock_get_lesson, \
         patch("src.context_builder.find_relevant_transcripts") as mock_find:
        mock_get_lesson.return_value = {
            "id": "M1L1",
            "title": "Character Bible",
            "content": "Build consistent characters",
        }
        mock_find.return_value = [(5, "boot1.json", "excerpt text")]

        from src.context_builder import assemble_context
        result = assemble_context("1", "1")

        assert isinstance(result, dict)
        assert "lesson_id" in result
        assert "lesson_title" in result
        assert "lesson_outline" in result
        assert "bootcamp_excerpts" in result
        assert result["lesson_id"] == "M1L1"
        assert "excerpt text" in result["bootcamp_excerpts"]


def test_assemble_context_calls_transcripts():
    with patch("src.context_builder.get_lesson") as mock_get_lesson, \
         patch("src.context_builder.find_relevant_transcripts") as mock_find:
        mock_get_lesson.return_value = {
            "id": "M1L1",
            "title": "Character Bible",
            "content": "Build consistent characters",
        }
        mock_find.return_value = [(5, "boot1.json", "excerpt text")]

        from src.context_builder import assemble_context
        assemble_context("1", "1")

        mock_find.assert_called_once()
        call_kwargs = mock_find.call_args
        # Check keyword arg or positional
        keywords_arg = call_kwargs[1].get("keywords", call_kwargs[0][0] if call_kwargs[0] else None)
        assert isinstance(keywords_arg, list)
        assert call_kwargs[1].get("max_results", call_kwargs[0][1] if len(call_kwargs[0]) > 1 else None) == 5
        assert call_kwargs[1].get("excerpt_chars", call_kwargs[0][2] if len(call_kwargs[0]) > 2 else None) == 1500


def test_save_script_path(tmp_path):
    with patch("src.context_builder.SCRIPTS_DIR", tmp_path), \
         patch("src.context_builder.set_status") as mock_set_status:
        from src.context_builder import save_script
        save_script("M1L1", "Character Bible", "script content")
        expected = tmp_path / "M1L1_character_bible.md"
        assert expected.exists()
        assert expected.read_text(encoding="utf-8") == "script content"


def test_save_sets_status(tmp_path):
    with patch("src.context_builder.SCRIPTS_DIR", tmp_path), \
         patch("src.context_builder.set_status") as mock_set_status:
        from src.context_builder import save_script
        save_script("M1L1", "Character Bible", "script content")
        mock_set_status.assert_called_once_with("M1L1", "scripted")


def test_list_modules():
    with patch("src.context_builder.load_course") as mock_load_course:
        mock_load_course.return_value = {
            "0": {"title": "Foundations", "lessons": {}},
            "1": {"title": "Character Creation", "lessons": {}},
        }
        from src.context_builder import list_modules
        result = list_modules()
        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            assert "num" in item
            assert "title" in item


def test_list_lessons_for_module():
    with patch("src.context_builder.load_course") as mock_load_course, \
         patch("src.context_builder.get_all") as mock_get_all:
        mock_load_course.return_value = {
            "0": {
                "title": "Foundations",
                "lessons": {
                    "1": {"id": "M0L1", "title": "Welcome", "content": "intro"},
                    "2": {"id": "M0L2", "title": "Challenge", "content": "48hr"},
                }
            }
        }
        mock_get_all.return_value = {
            "M0L1": {"status": "pending", "title": "Welcome"},
            "M0L2": {"status": "scripted", "title": "Challenge"},
        }
        from src.context_builder import list_lessons_for_module
        result = list_lessons_for_module("0")
        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            assert "id" in item
            assert "title" in item
            assert "status" in item
