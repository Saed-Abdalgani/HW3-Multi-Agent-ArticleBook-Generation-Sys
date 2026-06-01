"""Topic/language validation and run configuration for the content pipeline (M2+)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

from articlebook.shared.security_heuristics import assert_topic_and_language_safe

log = logging.getLogger(__name__)

TextDirection = Literal["rtl", "ltr"]

_TOPIC_MAX = 200
_LANG_MAX = 64
_DISALLOWED_IN_TOPIC = frozenset("\x00\n\r")


@dataclass(frozen=True)
class RunInputs:
    """Normalized CLI / API inputs for a pipeline run."""

    topic: str
    language: str
    text_direction: TextDirection


def normalize_text_direction(language: str) -> TextDirection:
    """Map primary language to base paragraph direction (Hebrew → RTL)."""
    key = language.strip().casefold()
    if key in {"hebrew", "he", "עברית", "iw"}:
        return "rtl"
    return "ltr"


def validate_topic_language(topic: str, language: str) -> RunInputs:
    """Validate and normalize topic and language; raise ValueError on invalid input."""
    t = topic.strip()
    lang = language.strip()
    if not t:
        raise ValueError("topic must be a non-empty string.")
    if len(t) > _TOPIC_MAX:
        raise ValueError(f"topic exceeds {_TOPIC_MAX} characters.")
    if not lang:
        raise ValueError("language must be a non-empty string.")
    if len(lang) > _LANG_MAX:
        raise ValueError(f"language exceeds {_LANG_MAX} characters.")
    if any(c in _DISALLOWED_IN_TOPIC for c in lang):
        raise ValueError("language must not contain newlines or NUL characters.")
    if any(c in _DISALLOWED_IN_TOPIC for c in t):
        raise ValueError("topic must not contain newlines or NUL characters.")
    assert_topic_and_language_safe(t, lang)
    direction = normalize_text_direction(lang)
    return RunInputs(topic=t, language=lang, text_direction=direction)


def log_resolved_run_config(
    inputs: RunInputs,
    *,
    mode: str,
    milestone: str,
    provider: str | None = None,
    model: str | None = None,
    seed: int | None = None,
    config_version: str | None = None,
) -> None:
    """Echo resolved configuration for traceability (NFR-8)."""
    log.info(
        "run.config mode=%s milestone=%s topic=%r language=%r text_direction=%s "
        "provider=%s model=%s seed=%s config_version=%s",
        mode,
        milestone,
        inputs.topic,
        inputs.language,
        inputs.text_direction,
        provider,
        model,
        seed,
        config_version,
    )
