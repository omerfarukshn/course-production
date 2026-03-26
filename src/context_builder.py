"""
Context builder — assembles lesson context from course outlines and bootcamp transcripts.
"""
import re
from pathlib import Path

from config import SCRIPTS_DIR
from src.course_loader import load_course, get_lesson
from src.transcript_loader import find_relevant_transcripts
from src.lesson_tracker import get_all, set_status


def extract_keywords(lesson_title: str, lesson_content: str) -> list[str]:
    """
    Extract search keywords from lesson title and content.

    Returns list of 1-10 lowercase strings, 4+ chars each, deduplicated.
    """
    combined = lesson_title + " " + lesson_content[:200]
    words = re.findall(r'\b[a-zA-Z]{4,}\b', combined)
    return list(dict.fromkeys(words))[:10]


def make_slug(title: str) -> str:
    """
    Convert lesson title to safe filename component.

    Examples:
        "Character Bible" -> "character_bible"
        "M0L3 — Tool Setup" -> "m0l3_tool_setup"
    """
    return re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')


def assemble_context(module_num: str, lesson_num: str) -> dict:
    """
    Assemble lesson context: outline + bootcamp transcript excerpts.

    Returns:
        {
            "lesson_id": str,
            "lesson_title": str,
            "lesson_outline": str,
            "bootcamp_excerpts": str,
        }

    Raises:
        ValueError: if lesson not found
    """
    lesson = get_lesson(module_num, lesson_num)
    if lesson is None:
        raise ValueError(f"Lesson not found: M{module_num}L{lesson_num}")

    keywords = extract_keywords(lesson["title"], lesson["content"])
    results = find_relevant_transcripts(keywords, max_results=5, excerpt_chars=1500)

    excerpt_parts = []
    for score, fname, excerpt in results:
        excerpt_parts.append(f"[Source: {fname}]\n{excerpt}")

    if excerpt_parts:
        bootcamp_text = "\n\n---\n\n".join(excerpt_parts)
    else:
        bootcamp_text = "(no relevant bootcamp transcripts found)"

    return {
        "lesson_id": lesson["id"],
        "lesson_title": lesson["title"],
        "lesson_outline": lesson["content"],
        "bootcamp_excerpts": bootcamp_text,
    }


def list_modules() -> list[dict]:
    """
    Return all modules sorted by module number.

    Returns:
        [{"num": "0", "title": "Foundations"}, ...]
    """
    course = load_course()
    return [
        {"num": mod_num, "title": mod_data["title"]}
        for mod_num, mod_data in sorted(course.items(), key=lambda x: float(x[0]))
    ]


def list_lessons_for_module(module_num: str) -> list[dict]:
    """
    Return all lessons for a module with status from lesson_tracker.

    Returns:
        [{"id": "M0L1", "title": "...", "lesson_num": "1", "status": "pending"}, ...]
    """
    course = load_course()
    module = course.get(module_num)
    if not module:
        return []

    all_statuses = get_all()
    result = []
    for les_num, les in sorted(module["lessons"].items(), key=lambda x: float(x[0])):
        result.append({
            "id": les["id"],
            "title": les["title"],
            "lesson_num": les_num,
            "status": all_statuses.get(les["id"], {}).get("status", "pending"),
        })
    return result


def save_script(lesson_id: str, lesson_title: str, script_text: str) -> Path:
    """
    Save approved script to SCRIPTS_DIR and mark lesson as scripted.

    Returns:
        Path to saved file
    """
    slug = make_slug(lesson_title)
    filename = f"{lesson_id}_{slug}.md"
    path = SCRIPTS_DIR / filename
    path.write_text(script_text, encoding="utf-8")
    set_status(lesson_id, "scripted")
    return path
