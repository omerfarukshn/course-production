# tests/test_review_ui.py — Unit test stubs for review UI (SCRPT-01, SCRPT-04)
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_skip_does_not_save():
    with patch("src.review_ui.Prompt") as mock_prompt_class, \
         patch("src.review_ui.save_script") as mock_save:
        mock_prompt_class.ask.return_value = "s"

        from src.review_ui import review_script
        review_script("M1L1", "Character Bible", "script text")

        mock_save.assert_not_called()


def test_accept_saves_script():
    with patch("src.review_ui.Prompt") as mock_prompt_class, \
         patch("src.review_ui.save_script") as mock_save:
        mock_prompt_class.ask.return_value = "a"
        mock_save.return_value = Path("scripts/M1L1_character_bible.md")

        from src.review_ui import review_script
        review_script("M1L1", "Character Bible", "script text")

        mock_save.assert_called_once_with("M1L1", "Character Bible", "script text")
