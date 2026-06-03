"""M9 observability: run reports and redaction."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from articlebook.shared.observability import (
    begin_articlebook_run,
    end_articlebook_run,
)
from articlebook.shared.observability_buffer import trace_get
from articlebook.shared.observability_redact import redact_for_report


def test_redact_strips_openai_style_key() -> None:
    t = redact_for_report("prefix sk-123456789012345678901234567890 suffix")
    assert "sk-123456789012345678901234567890" not in t
    assert "[REDACTED_SK]" in t


def test_redact_strips_google_gsk_style_key() -> None:
    t = redact_for_report("k=gsk_1234567890123456789012345678901234567890 end")
    assert "gsk_1234567890123456789012345678901234567890" not in t
    assert "[REDACTED_GSK]" in t


def test_begin_end_writes_pair(tmp_path: Path) -> None:
    log = logging.getLogger("test_m9")
    tok, rid = begin_articlebook_run(
        tmp_path,
        mode="llm",
        milestone="m2",
        topic="topic sk-123456789012345678901234567890",
        language="English",
        dry_run=False,
        logger=log,
    )
    buf = trace_get()
    assert buf is not None
    buf.append_task_output("line with sk-aaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    end_articlebook_run(
        tmp_path,
        tok,
        log,
        success=True,
        crew_result=None,
        error=None,
        qa_passed=None,
    )
    jp = tmp_path / "build" / f"run_report_{rid}.json"
    mp = tmp_path / "build" / f"run_report_{rid}.md"
    assert jp.is_file() and mp.is_file()
    blob = jp.read_text(encoding="utf-8")
    assert "sk-123456789012345678901234567890" not in blob
    assert "sk-aaaaaaaaaaaaaaaaaaaaaaaaaaaa" not in blob
    data = json.loads(blob)
    assert data["run_id"] == rid
    assert data["success"] is True
    assert data["task_outputs"]
