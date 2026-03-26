"""
Bootcamp transcript indexer — keyword-based relevance search.
"""
import json
import re
from pathlib import Path
from config import BOOTCAMP_TRANSCRIPTS


_cache = None

def _load() -> dict:
    global _cache
    if _cache is None:
        if not BOOTCAMP_TRANSCRIPTS.exists():
            return {}
        _cache = json.loads(BOOTCAMP_TRANSCRIPTS.read_text(encoding="utf-8"))
    return _cache


def _tokenize(text: str) -> set[str]:
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    stopwords = {
        "the", "and", "for", "that", "this", "with", "you", "your",
        "are", "have", "will", "from", "can", "its", "was", "not",
        "but", "they", "all", "been", "more", "when", "also", "into",
        "how", "what", "just", "make", "use", "get", "one", "out",
        "their", "then", "than", "about", "like", "some", "has",
        "would", "there", "which", "them", "here", "need"
    }
    return set(w for w in words if w not in stopwords)


def find_relevant_transcripts(
    keywords: list[str],
    max_results: int = 5,
    excerpt_chars: int = 1500,
) -> list[tuple]:
    """
    Search bootcamp transcripts by keyword relevance.

    Args:
        keywords: list of search terms (e.g. ["character consistency", "DNA"])
        max_results: how many to return
        excerpt_chars: how many characters of transcript to include in excerpt (default 1500)

    Returns:
        List of (score, filename, transcript_excerpt) sorted by score desc, then filename asc
    """
    data = _load()
    if not data:
        return []

    query_tokens = set()
    for kw in keywords:
        query_tokens.update(_tokenize(kw))

    scored = []
    for fname, info in data.items():
        transcript = info.get("transcript", "")
        if not transcript:
            continue
        doc_tokens = _tokenize(transcript)
        score = len(query_tokens & doc_tokens)
        if score > 0:
            excerpt = transcript[:excerpt_chars].strip()
            scored.append((score, fname, excerpt))

    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored[:max_results]


if __name__ == "__main__":
    results = find_relevant_transcripts(["character consistency", "DNA", "nano banana"])
    print(f"Top {len(results)} results:\n")
    for score, fname, excerpt in results:
        print(f"  [{score}] {fname}")
        print(f"       {excerpt[:120]}...\n")
