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
