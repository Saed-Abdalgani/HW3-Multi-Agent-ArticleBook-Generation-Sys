"""M6: compile journal, log scan, and PDF checks (mutates ``M6QAReport``)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from articlebook.m6_qa_parse import (
    RERUN_OR_UNDEFINED_SUMMARY,
    read_compile_journal,
    scan_log_for_link_citation_issues,
)
from articlebook.m6_qa_report import M6QAReport
from articlebook.m6_qa_surface import pdf_page_count, pdf_text_has_double_question


def apply_journal_log_pdf_checks(
    report: M6QAReport,
    *,
    build_dir: Path,
    resolved_prefix: str | None,
    allow_missing_pdf: bool,
    skip_page_count: bool,
    page_min: int,
    page_max: int,
) -> None:
    journal: dict[str, Any] | None = None
    if resolved_prefix:
        jp = build_dir / f"{resolved_prefix}_compile_journal.json"
        if jp.is_file():
            journal = read_compile_journal(build_dir, resolved_prefix)
    report.checks["compile_journal_ok"] = journal.get("ok") if journal else None
    if journal and not journal.get("ok"):
        err_cls = journal.get("error_class")
        if allow_missing_pdf and err_cls == "missing_engine":
            report.warnings.append(
                f"compile:journal_not_ok_ignored_under_allow_missing_pdf:{err_cls}"
            )
        else:
            report.errors.append(
                f"compile:journal_reports_failure:{journal.get('error_class')}"
                f":pass={journal.get('failure_pass')}"
            )
    elif journal is None:
        if resolved_prefix:
            report.warnings.append(f"compile:no_journal_file_for_prefix={resolved_prefix}")
        elif (build_dir / "main.pdf").is_file():
            report.warnings.append("compile:no_compile_journal_found_under_build")

    log_path = build_dir / "main.log"
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    ignore_stale_log = bool(
        allow_missing_pdf and journal and journal.get("error_class") == "missing_engine"
    )
    if ignore_stale_log:
        report.warnings.append("log:skipped_scan_stale_main.log_when_engine_missing")
        log_errs, log_warns = [], []
    else:
        log_errs, log_warns = scan_log_for_link_citation_issues(log_text)
    report.checks["log_undefined_lines_found"] = len(log_errs)
    report.errors.extend(f"log:{e[:400]}" for e in log_errs)
    report.warnings.extend(f"log_warn:{w}" for w in log_warns)

    if (
        log_text
        and not ignore_stale_log
        and RERUN_OR_UNDEFINED_SUMMARY.search(log_text)
        and journal
        and journal.get("ok")
    ):
        report.warnings.append("compile:log_still_contains_rerun_or_undefined_summary")

    pdf_path = build_dir / "main.pdf"
    if skip_page_count:
        report.checks["pdf_page_count"] = None
        report.checks["pdf_page_check"] = "skipped"
    elif pdf_path.is_file():
        n = pdf_page_count(pdf_path)
        report.checks["pdf_page_count"] = n
        if n is None:
            report.warnings.append("pdf:pypdf_unavailable_or_failed_open")
        elif not (page_min <= n <= page_max):
            report.errors.append(f"pdf:page_count_out_of_range:{n}_expected_{page_min}_{page_max}")
        leaked = pdf_text_has_double_question(pdf_path)
        report.checks["pdf_text_contains_double_question"] = leaked
        if leaked:
            report.warnings.append("pdf:extracted_text_contains_??_heuristic_unresolved_refs")
    else:
        report.checks["pdf_page_count"] = None
        if allow_missing_pdf:
            report.warnings.append("pdf:missing_build_main.pdf_(allow_missing_pdf)")
            report.checks["pdf_page_check"] = "skipped_no_pdf"
        else:
            report.errors.append("pdf:missing_build_main.pdf")
