"""M7 gatekeeper policy helpers and output validation."""

from __future__ import annotations

import pytest

from articlebook.shared.gatekeeper import estimate_cost_usd, is_transient_llm_error
from articlebook.shared.gatekeeper_policy import is_llm_route_failover_error, is_rate_limit_llm_error
from articlebook.shared.output_validate import (
    validate_agent_text_output,
    validate_agent_text_output_lenient,
)


def test_is_rate_limit_llm_error_heuristic() -> None:
    class RateLimitError(Exception):
        pass

    assert is_rate_limit_llm_error(RateLimitError("slow down"))
    assert is_rate_limit_llm_error(RuntimeError("429 too many requests"))
    assert is_rate_limit_llm_error(RuntimeError('OpenrouterException - {"code":402}'))
    assert is_rate_limit_llm_error(RuntimeError("This request requires more credits"))
    assert not is_rate_limit_llm_error(ValueError("bad prompt"))
    assert is_rate_limit_llm_error(RuntimeError("Resource exhausted"))


def test_is_llm_route_failover_includes_groq_tool_use_failed() -> None:
    body = 'GroqException - {"code":"tool_use_failed","message":"Failed to call a function"}'
    assert is_llm_route_failover_error(RuntimeError(body))


def test_is_llm_route_failover_includes_nvidia_single_tool_calls() -> None:
    body = "Nvidia_nimException - This model only supports single tool-calls at once!"
    assert is_llm_route_failover_error(RuntimeError(body))


def test_is_transient_llm_error_rejects_nvidia_single_tool_calls() -> None:
    assert not is_transient_llm_error(
        RuntimeError("This model only supports single tool-calls at once!")
    )


def test_is_transient_llm_error_rejects_tool_use_failed() -> None:
    assert not is_transient_llm_error(
        RuntimeError('tool_use_failed Failed to call a function. See failed_generation')
    )


def test_is_transient_llm_error_rejects_credit_exhaustion() -> None:
    class APIError(Exception):
        pass

    assert not is_transient_llm_error(
        APIError(
            'OpenrouterException - {"error":{"message":"requires more credits or fewer max_tokens"}}'
        )
    )
    assert is_transient_llm_error(APIError("OpenrouterException - 503 upstream busy"))


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
