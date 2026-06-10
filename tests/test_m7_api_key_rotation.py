"""Multi-key API failover on rate-limit style errors (M7 gatekeeper)."""

from __future__ import annotations

from crewai import LLM
from litellm.exceptions import RateLimitError

import articlebook.shared.gatekeeper_instrumented as gk_inst
from articlebook.shared.gatekeeper_instrumented import InstrumentedLLM
from articlebook.shared.gatekeeper_policy import should_reset_llm_route_chain_on_transient


def test_provider_suggested_retry_delay_seconds_groq_try_again_in() -> None:
    from articlebook.shared.gatekeeper_policy import provider_suggested_retry_delay_seconds

    msg = (
        'GroqException - Please try again in 10.402s. '
        "Limit 30000, Used 17735, Requested 17466"
    )
    d = provider_suggested_retry_delay_seconds(RuntimeError(msg))
    assert d is not None
    assert 10.4 <= d <= 11.2


def test_provider_suggested_retry_delay_seconds_none_when_missing() -> None:
    from articlebook.shared.gatekeeper_policy import provider_suggested_retry_delay_seconds

    assert provider_suggested_retry_delay_seconds(RuntimeError("503 unavailable")) is None


def test_instrumented_llm_transient_sleep_respects_groq_try_again_hint(monkeypatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(gk_inst.time, "sleep", lambda s: sleeps.append(float(s)))
    n = {"i": 0}

    def fake_llm_call(self: LLM, *args: object, **kwargs: object) -> str:
        n["i"] += 1
        if n["i"] < 2:
            raise RateLimitError(
                '{"message":"Please try again in 2.500s"}',
                llm_provider="groq",
                model="m-x",
            )
        return "ok"

    monkeypatch.setattr(gk_inst.LLM, "call", fake_llm_call)
    llm = InstrumentedLLM(
        gk_retry_max=5,
        gk_min_interval_s=0.0,
        gk_base_delay_s=0.01,
        gk_max_delay_s=30.0,
        gk_api_keys=["k1"],
        model="m-x",
        api_key="k1",
        temperature=0.0,
        seed=1,
    )
    assert llm.call(messages=[{"role": "user", "content": "p"}]) == "ok"
    assert len(sleeps) == 1
    assert sleeps[0] >= 2.5


def test_should_reset_llm_route_chain_on_transient_groq_request_too_large() -> None:
    exc = RuntimeError(
        'litellm.RateLimitError: GroqException - {"message":"Request too large for model '
        '`llama-3.1-8b-instant` ... Limit 6000, Requested 18919 ... reduce your message size"}'
    )
    assert should_reset_llm_route_chain_on_transient(exc) is True


def test_should_reset_llm_route_chain_on_transient_generic_503() -> None:
    assert should_reset_llm_route_chain_on_transient(RuntimeError("503 service unavailable")) is False


def test_instrumented_llm_resets_routes_after_groq_request_too_large_on_last_slot(monkeypatch) -> None:
    """Groq 'request too large' on the last route is transient; retry restarts from slot 1."""
    models: list[str] = []

    def fake_llm_call(self: LLM, *args: object, **kwargs: object) -> str:
        models.append(str(self.model))
        if str(self.model) == "m-a":
            if models.count("m-a") == 1:
                raise RuntimeError("Error code: 429 - rate limit exceeded")
            return "ok"
        if str(self.model) == "m-b":
            raise RateLimitError(
                "GroqException - Request too large for model `llama-3.1-8b-instant` "
                "... reduce your message size",
                llm_provider="groq",
                model="m-b",
            )
        raise AssertionError("unexpected model")

    monkeypatch.setattr(gk_inst.LLM, "call", fake_llm_call)

    llm = InstrumentedLLM(
        gk_retry_max=6,
        gk_min_interval_s=0.0,
        gk_base_delay_s=0.01,
        gk_llm_routes=[
            {"api_key": "k1", "model": "m-a"},
            {"api_key": "k2", "model": "m-b"},
        ],
        gk_api_keys=["k1", "k2"],
        model="m-a",
        api_key="k1",
        temperature=0.0,
        seed=1,
    )
    msg = [{"role": "user", "content": "ping"}]
    assert llm.call(messages=msg) == "ok"
    assert models == ["m-a", "m-b", "m-a"]


def test_instrumented_llm_rotates_to_next_key_on_rate_limit(monkeypatch) -> None:
    calls: list[str | None] = []

    def fake_llm_call(self: LLM, *args: object, **kwargs: object) -> str:
        calls.append(getattr(self, "api_key", None))
        if self.api_key == "k1":
            raise RuntimeError("Error code: 429 - rate limit exceeded")
        return "ok"

    monkeypatch.setattr(gk_inst.LLM, "call", fake_llm_call)

    llm = InstrumentedLLM(
        gk_retry_max=4,
        gk_min_interval_s=0.0,
        gk_api_keys=["k1", "k2"],
        model="gpt-4o-mini",
        api_key="k1",
        temperature=0.0,
        seed=1,
    )
    msg = [{"role": "user", "content": "ping"}]
    assert llm.call(messages=msg) == "ok"
    assert calls == ["k1", "k2"]


def test_instrumented_llm_llm_routes_rotate_key_and_model(monkeypatch) -> None:
    seen: list[tuple[str, str]] = []

    def fake_llm_call(self: LLM, *args: object, **kwargs: object) -> str:
        seen.append((str(self.api_key), str(self.model)))
        if str(self.model) == "m-a":
            raise RuntimeError("429 rate limit")
        return "ok"

    monkeypatch.setattr(gk_inst.LLM, "call", fake_llm_call)

    llm = InstrumentedLLM(
        gk_retry_max=4,
        gk_min_interval_s=0.0,
        gk_llm_routes=[
            {"api_key": "k1", "model": "m-a"},
            {"api_key": "k2", "model": "m-b"},
        ],
        gk_api_keys=["k1", "k2"],
        model="m-a",
        api_key="k1",
        temperature=0.0,
        seed=1,
    )
    msg = [{"role": "user", "content": "ping"}]
    assert llm.call(messages=msg) == "ok"
    assert seen[0] == ("k1", "m-a")
    assert seen[1] == ("k2", "m-b")


def test_instrumented_llm_llm_routes_rotate_on_openrouter_credits_error(monkeypatch) -> None:
    seen: list[tuple[str, str]] = []

    def fake_llm_call(self: LLM, *args: object, **kwargs: object) -> str:
        seen.append((str(self.api_key), str(self.model)))
        if str(self.model) == "m-or":
            raise RuntimeError(
                'APIError: OpenrouterException - {"error":{"message":"requires more credits"}}'
            )
        return "ok"

    monkeypatch.setattr(gk_inst.LLM, "call", fake_llm_call)

    llm = InstrumentedLLM(
        gk_retry_max=4,
        gk_min_interval_s=0.0,
        gk_llm_routes=[
            {"api_key": "k-or", "model": "m-or"},
            {"api_key": "k-gq", "model": "m-gq"},
        ],
        gk_api_keys=["k-or", "k-gq"],
        model="m-or",
        api_key="k-or",
        temperature=0.0,
        seed=1,
    )
    msg = [{"role": "user", "content": "ping"}]
    assert llm.call(messages=msg) == "ok"
    assert seen[0] == ("k-or", "m-or")
    assert seen[1] == ("k-gq", "m-gq")


def test_instrumented_llm_transient_retry_keeps_current_route(monkeypatch) -> None:
    """Regression: transient backoff on slot 2 must not reset to slot 1 (429 ping-pong)."""
    invocations: list[str] = []

    def fake_llm_call(self: LLM, *args: object, **kwargs: object) -> str:
        invocations.append(str(self.model))
        if str(self.model) == "m-a":
            raise RuntimeError("429 rate limit")
        if str(self.model) == "m-b" and invocations.count("m-b") == 1:
            raise RuntimeError("503 service unavailable")
        return "ok"

    monkeypatch.setattr(gk_inst.LLM, "call", fake_llm_call)

    llm = InstrumentedLLM(
        gk_retry_max=4,
        gk_min_interval_s=0.0,
        gk_llm_routes=[
            {"api_key": "k1", "model": "m-a"},
            {"api_key": "k2", "model": "m-b"},
        ],
        gk_api_keys=["k1", "k2"],
        model="m-a",
        api_key="k1",
        temperature=0.0,
        seed=1,
    )
    msg = [{"role": "user", "content": "ping"}]
    assert llm.call(messages=msg) == "ok"
    assert invocations[0] == "m-a"
    assert invocations[1] == "m-b"
    assert invocations[2] == "m-b"
    assert invocations.count("m-a") == 1


def test_instrumented_llm_llm_routes_rotate_on_groq_tool_use_failed(monkeypatch) -> None:
    seen: list[str] = []

    def fake_llm_call(self: LLM, *args: object, **kwargs: object) -> str:
        seen.append(str(self.model))
        if str(self.model) == "m-groq":
            raise RuntimeError(
                'BadRequestError: GroqException - {"code":"tool_use_failed",'
                '"message":"Failed to call a function"}'
            )
        return "ok"

    monkeypatch.setattr(gk_inst.LLM, "call", fake_llm_call)

    llm = InstrumentedLLM(
        gk_retry_max=4,
        gk_min_interval_s=0.0,
        gk_llm_routes=[
            {"api_key": "k-gq", "model": "m-groq"},
            {"api_key": "k-nv", "model": "m-nv"},
        ],
        gk_api_keys=["k-gq", "k-nv"],
        model="m-groq",
        api_key="k-gq",
        temperature=0.0,
        seed=1,
    )
    msg = [{"role": "user", "content": "ping"}]
    assert llm.call(messages=msg) == "ok"
    assert seen == ["m-groq", "m-nv"]
