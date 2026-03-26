"""Unit tests for src/lesson_tracker.py"""
import json
from unittest.mock import patch
from pathlib import Path


def test_get_status_default_pending():
    from src.lesson_tracker import get_status
    # Unknown lesson ID should return "pending"
    status = get_status("NONEXISTENT_LESSON_999")
    assert status == "pending"


def test_set_status_valid(tmp_path):
    """set_status writes correctly — isolated from real status file."""
    import src.lesson_tracker as lt
    fake_file = tmp_path / "lesson_status.json"
    with patch.object(lt, 'LESSON_STATUS_FILE', fake_file):
        lt.set_status("M0L1", "scripted")
        assert lt.get_status("M0L1") == "scripted"
        # Verify it actually wrote to the temp file
        assert fake_file.exists()
        data = json.loads(fake_file.read_text(encoding="utf-8"))
        assert data["M0L1"]["status"] == "scripted"


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


def test_init_idempotent():
    """Calling init_if_needed() twice does not duplicate entries."""
    from src.lesson_tracker import get_all
    first_call = get_all()   # calls init_if_needed() internally
    count_1 = len(first_call)
    second_call = get_all()  # calls init_if_needed() again
    count_2 = len(second_call)
    assert count_1 == count_2, f"init_if_needed not idempotent: {count_1} vs {count_2}"
    assert count_1 == 33, f"Expected 33 lessons, got {count_1}"
