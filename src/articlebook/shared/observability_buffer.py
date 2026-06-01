"""In-memory run trace bound to a ContextVar (M9)."""

from __future__ import annotations

import time
import uuid
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any

from articlebook.shared.observability_redact import redact_for_report

_ctx: ContextVar["RunTraceBuffer | None"] = ContextVar("articlebook_m9_trace", default=None)


@dataclass
class RunTraceBuffer:
    """Collects per-run facts for ``run_report_<run_id>``."""

    run_id: str
    started_monotonic: float
    meta: dict[str, Any]
    task_outputs: list[dict[str, Any]] = field(default_factory=list)
    llm_events: list[dict[str, Any]] = field(default_factory=list)
    _task_seq: int = 0

    def append_task_output(self, raw_output: str) -> None:
        self._task_seq += 1
        text = redact_for_report(raw_output, max_chars=2000)
        self.task_outputs.append(
            {
                "seq": self._task_seq,
                "output_chars": len(raw_output),
                "output_snippet": text.replace("\n", " ")[:800],
            }
        )

    def append_llm_event(self, row: dict[str, Any]) -> None:
        self.llm_events.append(row)

    def finish(
        self,
        *,
        success: bool,
        crew_result: str | None,
        error: str | None,
        extras: dict[str, Any] | None,
    ) -> dict[str, Any]:
        elapsed = time.perf_counter() - self.started_monotonic
        out: dict[str, Any] = {
            "run_id": self.run_id,
            "schema_version": "articlebook.m9.v1",
            "success": success,
            "elapsed_seconds": round(elapsed, 3),
            "meta": dict(self.meta),
            "task_outputs": list(self.task_outputs),
            "llm_calls": list(self.llm_events),
        }
        if crew_result is not None:
            out["crew_result"] = redact_for_report(crew_result, max_chars=8000)
        if error:
            out["error"] = redact_for_report(error, max_chars=2000)
        if extras:
            out["extras"] = extras
        return out


def trace_attach(buf: RunTraceBuffer) -> Token:
    return _ctx.set(buf)


def trace_get() -> RunTraceBuffer | None:
    return _ctx.get()


def trace_detach(token: Token) -> None:
    _ctx.reset(token)


def new_run_id() -> str:
    return uuid.uuid4().hex[:16]


def new_buffer(*, meta: dict[str, Any]) -> RunTraceBuffer:
    return RunTraceBuffer(run_id=new_run_id(), started_monotonic=time.perf_counter(), meta=meta)
