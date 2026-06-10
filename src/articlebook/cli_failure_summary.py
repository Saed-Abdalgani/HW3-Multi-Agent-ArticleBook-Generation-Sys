"""Terminal-friendly failure diagnosis after a CLI run (M9 run reports)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _truncate(s: str, max_chars: int) -> str:
    s = s.strip()
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 3].rstrip() + "..."


def _last_failed_llm_line(payload: dict[str, Any]) -> str | None:
    rows = payload.get("llm_calls")
    if not isinstance(rows, list):
        return None
    for row in reversed(rows):
        if not isinstance(row, dict):
            continue
        if row.get("ok") is False:
            return str(row)
    return None


def _load_run_report_json(root: Path, run_id: str) -> dict[str, Any] | None:
    path = root / "build" / f"run_report_{run_id}.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def print_cli_failure_summary(
    *,
    root: Path,
    run_id: str | None,
    error_message: str | None,
    qa_passed: bool | None,
    milestone: str,
) -> None:
    """Print a single bordered block with the most actionable failure lines."""
    bar = "=" * 78
    print("\n" + bar)
    print(" RUN FAILED — diagnosis (copy this block when asking for help)")
    print(bar)
    print(f"  milestone:     {milestone}")
    print(f"  qa_passed:     {qa_passed}")
    if error_message:
        print("  exception:")
        for ln in _truncate(error_message, 6000).splitlines():
            print(f"    {ln}")
    else:
        print("  exception:     (not captured here — scroll up for Python traceback)")
    payload: dict[str, Any] | None = None
    if run_id:
        payload = _load_run_report_json(root, run_id)
        md_rel = f"build/run_report_{run_id}.md"
        json_rel = f"build/run_report_{run_id}.json"
        print(f"  run_report:     {json_rel}")
        print(f"                  {md_rel}")
    if payload:
        rep_err = payload.get("error")
        if isinstance(rep_err, str) and rep_err.strip():
            if rep_err.strip() != (error_message or "").strip():
                print("  run_report.error:")
                for ln in _truncate(rep_err, 4000).splitlines():
                    print(f"    {ln}")
        llm_fail = _last_failed_llm_line(payload)
        if llm_fail:
            print("  last_failed_llm_call (instrumented gatekeeper):")
            for ln in _truncate(llm_fail, 4000).splitlines():
                print(f"    {ln}")
    elif run_id:
        print("  (run report JSON missing or unreadable)")
    print(bar + "\n")
