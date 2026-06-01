"""Thin CLI entrypoint for milestones M1–M6 (stub + LLM)."""

from __future__ import annotations

import argparse
import logging

from articlebook.cli_execution import run_articlebook_cli_body
from articlebook.cli_preflight import reset_cli_security_tokens, run_cli_security_preflight
from articlebook.pipeline import setup_logging
from articlebook.shared.observability import begin_articlebook_run, end_articlebook_run
from articlebook.shared.paths import project_root


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-agent article/book generation (CrewAI + LaTeX, HW3)."
    )
    parser.add_argument("--topic", required=True, help="Document topic")
    parser.add_argument(
        "--language",
        required=True,
        help="Primary language (e.g., English or Hebrew)",
    )
    parser.add_argument(
        "--milestone",
        choices=("m1", "m2", "m3", "m4", "m5", "m6"),
        default="m2",
        help="m1=full smoke; m2=content; m3=M2+figures; m4=M3+LaTeX+compile; "
        "m5=M4+canonical multipass (biber); m6=M5+deterministic QA contract. Default: m2.",
    )
    parser.add_argument(
        "--stub",
        action="store_true",
        help="Offline deterministic run (no LLM). Milestone selects stub profile.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="M8: skip disk writes for stub pipelines; crew write_workspace_file is no-op.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="M8: skip interactive paid-run and overwrite confirmations (CI/automation).",
    )
    parser.add_argument(
        "--m6-allow-missing-pdf",
        action="store_true",
        help=(
            "For m6: relax PDF / missing-engine compile journal so static checks run "
            "without MiKTeX."
        ),
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    log = logging.getLogger(__name__)
    root = project_root()
    t_dry, t_allow = run_cli_security_preflight(args, root)
    m9_tok, _run_id = begin_articlebook_run(
        root,
        mode="stub" if args.stub else "llm",
        milestone=args.milestone,
        topic=args.topic,
        language=args.language,
        dry_run=args.dry_run,
        logger=log,
    )
    ok = False
    crew_summary: str | None = None
    qa_passed: bool | None = None
    err: str | None = None
    rid: str | None = None
    try:
        ok, crew_summary, qa_passed = run_articlebook_cli_body(args, log)
    except SystemExit as se:
        code = se.code
        ok = code is None or code is False or code == 0
        err = f"SystemExit:{code!r}"
        raise
    except BaseException as exc:
        ok = False
        err = f"{type(exc).__name__}:{exc}"
        raise
    finally:
        try:
            rid = end_articlebook_run(
                root,
                m9_tok,
                log,
                success=ok,
                crew_result=crew_summary,
                error=err,
                qa_passed=qa_passed,
            )
        finally:
            reset_cli_security_tokens(t_dry, t_allow)
        if rid:
            print(
                f"\nRun report: build/run_report_{rid}.json  "
                f"(markdown: build/run_report_{rid}.md)"
            )


if __name__ == "__main__":
    main()
