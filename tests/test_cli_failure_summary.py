"""CLI failure diagnosis helpers."""

from __future__ import annotations

import json
from pathlib import Path

from articlebook.cli_failure_summary import _last_failed_llm_line, _load_run_report_json


def test_last_failed_llm_line_picks_last_false(tmp_path: Path) -> None:
    p = tmp_path / "run_report_x.json"
    p.write_text(
        json.dumps(
            {
                "llm_calls": [
                    {"ok": True, "attempt": 1},
                    {"ok": False, "message": "first fail"},
                    {"ok": True, "attempt": 1},
                    {"ok": False, "message": "last fail"},
                ]
            }
        ),
        encoding="utf-8",
    )
    data = json.loads(p.read_text(encoding="utf-8"))
    line = _last_failed_llm_line(data)
    assert line is not None
    assert "last fail" in line
    assert "first fail" not in line


def test_load_run_report_json_reads_build(tmp_path: Path) -> None:
    rid = "abc123"
    build = tmp_path / "build"
    build.mkdir(parents=True)
    (build / f"run_report_{rid}.json").write_text(
        '{"run_id":"abc123","llm_calls":[]}', encoding="utf-8"
    )
    got = _load_run_report_json(tmp_path, rid)
    assert got is not None
    assert got.get("run_id") == "abc123"
