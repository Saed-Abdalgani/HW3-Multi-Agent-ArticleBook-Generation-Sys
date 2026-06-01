"""Write ``build/run_report_<run_id>.{json,md}`` (M9)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_run_report_pair(root: Path, run_id: str, payload: dict[str, Any]) -> tuple[Path, Path]:
    """Persist JSON + Markdown summaries under ``build/``."""
    build = root / "build"
    build.mkdir(parents=True, exist_ok=True)
    jp = build / f"run_report_{run_id}.json"
    mp = build / f"run_report_{run_id}.md"
    jp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    mp.write_text(_markdown_for_run(payload), encoding="utf-8")
    return jp, mp


def _markdown_for_run(payload: dict[str, Any]) -> str:
    meta = payload.get("meta") or {}
    lines = [
        "# Articlebook run report (M9)",
        "",
        f"- **run_id:** `{payload.get('run_id')}`",
        f"- **success:** {payload.get('success')}",
        f"- **elapsed_seconds:** {payload.get('elapsed_seconds')}",
        f"- **mode / milestone:** {meta.get('mode')} / {meta.get('milestone')}",
        f"- **wall_start_utc:** {meta.get('wall_start_utc')}",
        "",
        "## Meta",
        "",
        "```json",
        json.dumps(meta, indent=2, ensure_ascii=False),
        "```",
        "",
        "## LLM calls (instrumented gatekeeper)",
        "",
    ]
    for row in payload.get("llm_calls") or []:
        lines.append(f"- {row}")
    lines.extend(["", "## Task output snippets (redacted)", ""])
    for row in payload.get("task_outputs") or []:
        snip = row.get("output_snippet")
        lines.append(
            f"- seq={row.get('seq')} chars={row.get('output_chars')}: `{snip}`"
        )
    if payload.get("crew_result"):
        cr = str(payload["crew_result"])[:4000]
        lines.extend(
            ["", "## Crew result (redacted, truncated)", "", "```", cr, "```"]
        )
    if payload.get("error"):
        lines.extend(["", "## Error", "", str(payload["error"])])
    if payload.get("extras"):
        ej = json.dumps(payload["extras"], indent=2)
        lines.extend(["", "## Extras", "", "```json", ej, "```"])
    lines.append("")
    return "\n".join(lines)
