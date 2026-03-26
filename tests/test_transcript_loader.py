"""Unit tests for src/transcript_loader.py"""
from src.transcript_loader import find_relevant_transcripts


def test_find_relevant_returns_list():
    results = find_relevant_transcripts(["character", "consistency"])
    assert isinstance(results, list)


def test_find_relevant_max_results():
    results = find_relevant_transcripts(["character", "nano banana"], max_results=3)
    assert len(results) <= 3


def test_find_relevant_result_tuple_structure():
    results = find_relevant_transcripts(["character", "consistency"])
    if results:  # only test structure if bootcamp_transcripts.json exists
        score, fname, excerpt = results[0]
        assert isinstance(score, int)
        assert isinstance(fname, str)
        assert isinstance(excerpt, str)


def test_find_relevant_empty_keywords():
    results = find_relevant_transcripts([])
    assert isinstance(results, list)


def test_find_relevant_excerpt_chars():
    """excerpt_chars parameter controls excerpt length."""
    short = find_relevant_transcripts(["character", "consistency"], excerpt_chars=200)
    if short:
        assert len(short[0][2]) <= 200, f"Excerpt should be <= 200 chars, got {len(short[0][2])}"

    long = find_relevant_transcripts(["character", "consistency"], excerpt_chars=3000)
    if long:
        assert len(long[0][2]) > 500, f"Excerpt should be > 500 chars with excerpt_chars=3000, got {len(long[0][2])}"


def test_find_relevant_deterministic():
    """Same query always returns same order (secondary sort by filename)."""
    query = ["character", "consistency", "DNA", "nano banana"]
    run1 = find_relevant_transcripts(query)
    run2 = find_relevant_transcripts(query)
    assert run1 == run2, "Results should be identical across calls"
    if len(run1) >= 2:
        # Verify secondary sort: if scores are equal, filenames are ascending
        for i in range(len(run1) - 1):
            if run1[i][0] == run1[i+1][0]:
                assert run1[i][1] <= run1[i+1][1], (
                    f"Tied scores should sort by filename: {run1[i][1]} > {run1[i+1][1]}"
                )
