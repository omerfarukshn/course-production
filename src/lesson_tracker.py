"""
Lesson status tracker — persists per-lesson status to JSON.
Status values: pending | scripted | audio_done
"""
import json
from pathlib import Path
from config import LESSON_STATUS_FILE
from src.course_loader import list_all_lessons


def _load_raw() -> dict:
    if LESSON_STATUS_FILE.exists():
        return json.loads(LESSON_STATUS_FILE.read_text(encoding="utf-8"))
    return {}


def _save(data: dict):
    LESSON_STATUS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def init_if_needed():
    """Create status entries for every lesson that doesn't have one yet."""
    data = _load_raw()
    changed = False
    for lesson in list_all_lessons():
        lid = lesson["id"]
        if lid not in data:
            data[lid] = {"status": "pending", "title": lesson["title"]}
            changed = True
    if changed:
        _save(data)


def get_status(lesson_id: str) -> str:
    """Returns 'pending' | 'scripted' | 'audio_done'"""
    data = _load_raw()
    return data.get(lesson_id, {}).get("status", "pending")


def set_status(lesson_id: str, status: str):
    valid = {"pending", "scripted", "audio_done"}
    if status not in valid:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid}")
    data = _load_raw()
    if lesson_id not in data:
        data[lesson_id] = {}
    data[lesson_id]["status"] = status
    _save(data)


def get_all() -> dict:
    """Returns {lesson_id: {status, title}} for all lessons."""
    init_if_needed()
    return _load_raw()


if __name__ == "__main__":
    init_if_needed()
    all_lessons = get_all()
    counts = {"pending": 0, "scripted": 0, "audio_done": 0}
    for lid, info in all_lessons.items():
        counts[info["status"]] += 1
    print(f"Lesson status initialized: {len(all_lessons)} lessons")
    for status, count in counts.items():
        print(f"  {status}: {count}")
