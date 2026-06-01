"""M9 observability: run_id, structured log lines, and ``build/run_report_*`` artifacts."""

from __future__ import annotations

import json
import logging
from contextvars import Token
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from articlebook.shared.observability_buffer import (
    new_buffer,
    trace_attach,
    trace_detach,
    trace_get,
)
from articlebook.shared.observability_emit import write_run_report_pair
from articlebook.shared.observability_redact import redact_for_report

__all__ = [
    "append_task_output_if_tracing",
    "begin_articlebook_run",
    "end_articlebook_run",
    "log_json_event",
]


def log_json_event(logger: logging.Logger, event: str, **fields: object) -> None:
    """Emit a single-line JSON payload for log aggregators (NFR-8)."""
    payload = {"event": event, **fields}
    logger.info("obs.%s %s", event, json.dumps(payload, default=str, ensure_ascii=False))


def begin_articlebook_run(
    root: Path,
    *,
    mode: str,
    milestone: str,
    topic: str,
    language: str,
    dry_run: bool,
    logger: logging.Logger,
) -> tuple[Token, str]:
    """Start tracing; returns ``(context_token, run_id)``."""
    meta: dict[str, Any] = {
        "wall_start_utc": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "milestone": milestone,
        "language": language,
        "topic_preview": redact_for_report(topic[:160], max_chars=200),
        "dry_run": dry_run,
        "project_root": str(root.resolve()),
    }
    buf = new_buffer(meta=meta)
    tok = trace_attach(buf)
    log_json_event(logger, "run_begin", run_id=buf.run_id, milestone=milestone, mode=mode)
    return tok, buf.run_id


def append_task_output_if_tracing(raw: object) -> None:
    buf = trace_get()
    if buf is not None:
        buf.append_task_output(str(raw))


def _extras(root: Path, qa_passed: bool | None) -> dict[str, Any]:
    arts: dict[str, bool] = {}
    checks = (
        ("resolved_run_config", root / "build" / "resolved_run_config.json"),
        ("m6_qa_report_md", root / "build" / "m6_qa_report.md"),
        ("m6_qa_report_json", root / "build" / "m6_qa_report.json"),
    )
    for key, path in checks:
        arts[key] = path.is_file()
    return {
        "wall_end_utc": datetime.now(timezone.utc).isoformat(),
        "qa_passed": qa_passed,
        "artifacts": arts,
    }


def end_articlebook_run(
    root: Path,
    token: Token,
    logger: logging.Logger,
    *,
    success: bool,
    crew_result: str | None,
    error: str | None,
    qa_passed: bool | None,
) -> str | None:
    """Finalize buffer, write JSON+Markdown under ``build/``, detach context."""
    buf = trace_get()
    if buf is None:
        trace_detach(token)
        return None
    extras = _extras(root, qa_passed)
    payload = buf.finish(
        success=success,
        crew_result=crew_result,
        error=error,
        extras=extras,
    )
    trace_detach(token)
    jp, mp = write_run_report_pair(root, buf.run_id, payload)
    log_json_event(
        logger,
        "run_end",
        run_id=buf.run_id,
        success=success,
        json_report=str(jp.relative_to(root)),
        md_report=str(mp.relative_to(root)),
    )
    return buf.run_id
