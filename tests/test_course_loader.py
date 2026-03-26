"""Unit tests for src/course_loader.py"""
from src.course_loader import load_course, list_all_lessons, get_lesson


def test_load_course_returns_modules():
    course = load_course()
    assert len(course) >= 6, f"Expected >= 6 modules (M0-M5), got {len(course)}"


def test_load_course_has_module_0():
    course = load_course()
    assert "0" in course
    assert "title" in course["0"]
    assert "lessons" in course["0"]


def test_list_all_lessons_count():
    lessons = list_all_lessons()
    assert len(lessons) == 33, f"Expected 33 lessons, got {len(lessons)}"


def test_list_all_lessons_has_required_keys():
    lessons = list_all_lessons()
    first = lessons[0]
    for key in ["module", "module_title", "lesson", "id", "title", "content"]:
        assert key in first, f"Missing key: {key}"


def test_get_lesson_returns_dict():
    lesson = get_lesson("1", "1")
    assert lesson is not None
    assert "id" in lesson
    assert lesson["id"] == "M1L1"


def test_get_lesson_invalid_returns_none():
    lesson = get_lesson("99", "99")
    assert lesson is None
