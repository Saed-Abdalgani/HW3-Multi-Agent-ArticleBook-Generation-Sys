"""Multi-key API failover on rate-limit style errors (M7 gatekeeper)."""

from __future__ import annotations

from crewai import LLM

import articlebook.shared.gatekeeper_instrumented as gk_inst
from articlebook.shared.gatekeeper_instrumented import InstrumentedLLM


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
