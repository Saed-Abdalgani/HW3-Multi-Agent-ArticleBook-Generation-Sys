"""M7 gatekeeper policy helpers and output validation."""

from __future__ import annotations

import pytest

from articlebook.shared.gatekeeper import estimate_cost_usd, is_transient_llm_error
from articlebook.shared.output_validate import (
    validate_agent_text_output,
    validate_agent_text_output_lenient,
)


def test_is_transient_llm_error_heuristic() -> None:
    class RateLimitError(Exception):
        pass

    assert is_transient_llm_error(RateLimitError("slow down"))
    assert is_transient_llm_error(RuntimeError("429 too many requests"))
    assert not is_transient_llm_error(ValueError("bad prompt"))


def test_estimate_cost_usd() -> None:
    delta = {"prompt_tokens": 1_000_000, "completion_tokens": 0, "total_tokens": 1_000_000}
    pricing = {"input": 2.0, "output": 6.0}
    assert estimate_cost_usd(delta, pricing) == pytest.approx(2.0)


def test_validate_agent_text_output_helpers() -> None:
    with pytest.raises(ValueError):
        validate_agent_text_output("   ")
    assert validate_agent_text_output_lenient("   ") is None
    assert validate_agent_text_output_lenient(" ok ") == "ok"
