"""Strip CrewAI/LiteLLM message keys that strict APIs (Groq) reject."""

from __future__ import annotations

from articlebook.shared.gatekeeper_instrumented import strip_provider_specific_message_keys


def test_strip_cache_breakpoint_from_messages() -> None:
    raw = [
        {"role": "system", "content": "x", "cache_breakpoint": True},
        {"role": "user", "content": "hi"},
    ]
    out = strip_provider_specific_message_keys(raw)
    assert out[0] == {"role": "system", "content": "x"}
    assert out[1] == {"role": "user", "content": "hi"}
    assert "cache_breakpoint" in raw[0]
    assert "cache_breakpoint" not in out[0]


def test_strip_leaves_strings() -> None:
    assert strip_provider_specific_message_keys("plain") == "plain"
