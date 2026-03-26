# tests/test_script_generator.py — Unit tests for script_generator module (SCRPT-03, SCRPT-06)
import pytest
from unittest.mock import patch, MagicMock


def _make_mock_response(text="Generated script"):
    """Helper: build a mock Anthropic response object."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=text)]
    mock_response.usage.cache_creation_input_tokens = 100
    mock_response.usage.cache_read_input_tokens = 0
    mock_response.usage.input_tokens = 500
    mock_response.usage.output_tokens = 200
    return mock_response


def test_missing_api_key():
    import src.script_generator as sg
    # Reset lazy client so it re-checks env
    sg._client = None

    with patch.dict("os.environ", {}, clear=True):
        if "ANTHROPIC_API_KEY" in __import__("os").environ:
            import os
            os.environ.pop("ANTHROPIC_API_KEY", None)
        # Patch os.environ.get to return None for the key
        with patch("src.script_generator.os") as mock_os:
            mock_os.environ.get.return_value = None
            sg._client = None
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                sg.generate_script("outline", "excerpts")


def test_message_structure():
    import src.script_generator as sg
    sg._client = None

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_response()

    with patch("src.script_generator.Anthropic", return_value=mock_client), \
         patch("src.script_generator.os") as mock_os:
        mock_os.environ.get.return_value = "test-key"
        sg._client = None

        result = sg.generate_script("lesson outline", "bootcamp excerpts")

    mock_client.messages.create.assert_called_once()
    call_kwargs = mock_client.messages.create.call_args[1]
    assert call_kwargs.get("model") == "claude-haiku-4-5-20251001"

    system = call_kwargs.get("system")
    assert isinstance(system, list)
    assert len(system) == 1
    # The system block must have cache_control
    block = system[0]
    # TextBlockParam or dict — check attribute or key
    if hasattr(block, "cache_control"):
        assert block.cache_control is not None
    else:
        assert "cache_control" in block

    messages = call_kwargs.get("messages")
    user_content = messages[0]["content"]
    assert isinstance(user_content, list)
    assert len(user_content) == 2
    # First content block has cache_control
    first = user_content[0]
    assert "cache_control" in first


def test_cache_control_param():
    import src.script_generator as sg
    sg._client = None

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_response()

    with patch("src.script_generator.Anthropic", return_value=mock_client), \
         patch("src.script_generator.os") as mock_os:
        mock_os.environ.get.return_value = "test-key"
        sg._client = None

        sg.generate_script("outline", "excerpts")

    call_kwargs = mock_client.messages.create.call_args[1]

    # System block cache_control
    system_block = call_kwargs["system"][0]
    if hasattr(system_block, "cache_control"):
        assert system_block.cache_control == {"type": "ephemeral"}
    else:
        assert system_block["cache_control"] == {"type": "ephemeral"}

    # First user content block cache_control
    first_user_block = call_kwargs["messages"][0]["content"][0]
    assert first_user_block["cache_control"] == {"type": "ephemeral"}


def test_revision_note_appended():
    import src.script_generator as sg
    sg._client = None

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_response()

    with patch("src.script_generator.Anthropic", return_value=mock_client), \
         patch("src.script_generator.os") as mock_os:
        mock_os.environ.get.return_value = "test-key"
        sg._client = None

        sg.generate_script("outline", "excerpts", revision_note="more examples")

    call_kwargs = mock_client.messages.create.call_args[1]
    user_content = call_kwargs["messages"][0]["content"]
    # Second block contains the revision note
    second_block_text = user_content[1]["text"]
    assert "Revision note: more examples" in second_block_text


def test_generate_returns_text():
    import src.script_generator as sg
    sg._client = None

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_response("Generated script")

    with patch("src.script_generator.Anthropic", return_value=mock_client), \
         patch("src.script_generator.os") as mock_os:
        mock_os.environ.get.return_value = "test-key"
        sg._client = None

        result = sg.generate_script("outline", "excerpts")

    assert result == "Generated script"
