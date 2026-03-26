"""Unit tests for src/lesson_tracker.py"""
import json
import tempfile
import os
from unittest.mock import patch
from pathlib import Path


def test_get_status_default_pending():
    from src.lesson_tracker import get_status
    # Unknown lesson ID should return "pending"
    status = get_status("NONEXISTENT_LESSON_999")
    assert status == "pending"


def test_set_status_valid():
    from src.lesson_tracker import set_status, get_status
    # Set a test lesson to "scripted" then verify
    set_status("M0L1", "scripted")
    assert get_status("M0L1") == "scripted"
    # Reset back to pending
    set_status("M0L1", "pending")


def test_set_status_invalid_raises():
    from src.lesson_tracker import set_status
    import pytest
    with pytest.raises(ValueError):
        set_status("M0L1", "invalid_status")


def test_get_all_returns_dict():
    from src.lesson_tracker import get_all
    all_lessons = get_all()
    assert isinstance(all_lessons, dict)
    assert len(all_lessons) > 0


def test_get_all_has_status_key():
    from src.lesson_tracker import get_all
    all_lessons = get_all()
    for lid, info in all_lessons.items():
        assert "status" in info, f"Missing 'status' key for {lid}"
