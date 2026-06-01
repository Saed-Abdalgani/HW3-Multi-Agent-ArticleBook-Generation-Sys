from __future__ import annotations

import pytest

from articlebook.inputs import normalize_text_direction, validate_topic_language


def test_validate_topic_language_ok() -> None:
    r = validate_topic_language("  Agents + LaTeX  ", "English")
    assert r.topic == "Agents + LaTeX"
    assert r.language == "English"
    assert r.text_direction == "ltr"


def test_hebrew_language_rtl() -> None:
    r = validate_topic_language("נושא", "Hebrew")
    assert r.text_direction == "rtl"
    assert normalize_text_direction("עברית") == "rtl"


def test_validate_rejects_empty_topic() -> None:
    with pytest.raises(ValueError, match="topic"):
        validate_topic_language("   ", "en")


def test_validate_rejects_newline_in_topic() -> None:
    with pytest.raises(ValueError, match="newline"):
        validate_topic_language("bad\ninjection", "English")


def test_validate_rejects_newline_in_language() -> None:
    with pytest.raises(ValueError, match="language"):
        validate_topic_language("OK", "bad\nlang")


def test_validate_rejects_prompt_injection_topic() -> None:
    with pytest.raises(ValueError, match="security heuristics"):
        validate_topic_language("Topic about jailbreak override safety please", "English")
