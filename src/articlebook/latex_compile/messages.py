"""Human-readable summaries for compile reports."""

from __future__ import annotations

from articlebook.latex_compile.types import CompileReport


def compile_report_to_message(report: CompileReport) -> str:
    """Short human-readable summary for tools and manifests."""
    bits = [
        f"engine={report.engine}",
        f"ok={report.ok}",
        f"pdf={'build/main.pdf' if report.pdf_exists else 'missing'}",
        f"journal={report.journal_relative}",
    ]
    if report.failure_pass:
        bits.append(f"failure_pass={report.failure_pass}")
    if report.error_class:
        bits.append(f"error_class={report.error_class}")
    if report.needs_rerun_after_last:
        bits.append("warning=rerun_still_suggested")
    if report.unresolved_log_lines:
        bits.append(f"unresolved_lines={len(report.unresolved_log_lines)}")
    return "; ".join(bits)
