"""
Course loader — parses sahinlabs_course.txt into structured lessons.
"""
import re
from pathlib import Path
from config import COURSE_FILE


def load_course() -> dict:
    """
    Returns:
        {
            "M0": {
                "title": "Foundations",
                "lessons": {
                    "L1": {"id": "M0L1", "title": "...", "content": "..."},
                    ...
                }
            },
            ...
        }
    """
    if not COURSE_FILE.exists():
        print(f"\n[ERROR] Course file not found: {COURSE_FILE}")
        print("  Ömer: sahinlabs_course.txt dosyasını sources/ klasörüne koy.")
        return {}

    text = COURSE_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()

    modules = {}
    current_module = None
    current_lesson = None
    content_lines = []

    module_re = re.compile(r'^MODULE\s+(\d+):\s+(.+)')
    lesson_re = re.compile(r'^L(\d+(?:\.\d+)?):\s+(.+)')

    def save_lesson():
        if current_module and current_lesson:
            lesson_id, title = current_lesson
            modules[current_module]["lessons"][lesson_id] = {
                "id": f"M{current_module}L{lesson_id}",
                "title": title,
                "content": "\n".join(content_lines).strip(),
            }

    for line in lines:
        m = module_re.match(line.strip())
        if m:
            save_lesson()
            current_lesson = None
            content_lines = []
            current_module = m.group(1)
            modules[current_module] = {
                "title": m.group(2).strip(),
                "lessons": {}
            }
            continue

        if current_module:
            l = lesson_re.match(line.strip())
            if l:
                save_lesson()
                content_lines = []
                current_lesson = (l.group(1), l.group(2).strip())
                continue

            if current_lesson:
                content_lines.append(line)

    save_lesson()
    return modules


def get_lesson(module_num: str, lesson_num: str) -> dict | None:
    """
    get_lesson("1", "1") → lesson dict or None
    get_lesson("0", "3") → M0L3
    """
    course = load_course()
    mod = course.get(module_num)
    if not mod:
        return None
    return mod["lessons"].get(lesson_num)


def list_all_lessons() -> list[dict]:
    """Returns flat list of all lessons with id, title, module."""
    course = load_course()
    result = []
    for mod_num, mod_data in sorted(course.items(), key=lambda x: float(x[0])):
        for les_num, les_data in sorted(mod_data["lessons"].items(), key=lambda x: float(x[0])):
            result.append({
                "module": mod_num,
                "module_title": mod_data["title"],
                "lesson": les_num,
                "id": les_data["id"],
                "title": les_data["title"],
                "content": les_data["content"],
            })
    return result


if __name__ == "__main__":
    lessons = list_all_lessons()
    print(f"Toplam {len(lessons)} ders yüklendi.\n")
    for l in lessons:
        preview = l["content"][:60].replace("\n", " ")
        print(f"  [{l['id']}] {l['title']}")
        print(f"       {preview}...")
