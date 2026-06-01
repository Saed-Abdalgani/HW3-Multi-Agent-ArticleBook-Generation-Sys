"""Format M6 contract QA results for the CrewAI ``run_m6_contract_checks`` tool."""

from __future__ import annotations

from articlebook.m6_qa_report import M6QAReport


def m6_contract_tool_reply(report: M6QAReport, log_prefix: str) -> str:
    """Human-readable summary for agent tool return (truncated lists)."""
    status = "PASS" if report.passed else "FAIL"
    head = f"M6 contract QA: **{status}** (prefix={log_prefix}).\n"
    if report.errors:
        head += "Errors:\n- " + "\n- ".join(report.errors[:25])
        if len(report.errors) > 25:
            head += f"\n- … ({len(report.errors) - 25} more)"
        head += "\n"
    if report.warnings:
        head += "Warnings:\n- " + "\n- ".join(report.warnings[:15])
        if len(report.warnings) > 15:
            head += f"\n- … ({len(report.warnings) - 15} more)"
    head += "\nSee `build/m6_qa_report.md`."
    return head
