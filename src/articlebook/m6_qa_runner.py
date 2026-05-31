"""M6: orchestrate contract QA and write ``build/m6_qa_report.*``."""

from __future__ import annotations

import json
import re
from pathlib import Path

from articlebook.m3_assets import verify_m3_figure_assets
from articlebook.m6_qa_build_phase import apply_journal_log_pdf_checks
from articlebook.m6_qa_parse import (
    collect_tex_sources,
    extract_cite_keys_from_tex,
    parse_bib_keys,
    resolve_compile_log_prefix,
    verify_graphics_resolve,
)
from articlebook.m6_qa_report import M6QAReport
from articlebook.m6_qa_surface import (
    bidi_heuristic,
    fr9_source_checks,
    front_matter_list_checks,
    main_tex_structure_checks,
    scan_build_for_secrets,
)


def run_m6_contract_qa(
    root: Path,
    *,
    log_prefix: str | None = None,
    page_min: int = 15,
    page_max: int = 20,
    skip_page_count: bool = False,
    allow_missing_pdf: bool = False,
) -> M6QAReport:
    """Run FR-20 / prd §9 checks; write ``build/m6_qa_report.md`` and ``.json``."""
    root = root.resolve()
    build_dir = root / "build"
    latex_dir = root / "latex"
    content_dir = root / "content"
    build_dir.mkdir(parents=True, exist_ok=True)

    resolved_prefix = resolve_compile_log_prefix(build_dir, log_prefix)
    report = M6QAReport(passed=True, log_prefix_used=resolved_prefix or log_prefix, checks={})

    m3_ok, m3_issues = verify_m3_figure_assets(root)
    report.checks["m3_assets_ok"] = m3_ok
    if not m3_ok:
        report.errors.extend(f"m3:{issue}" for issue in m3_issues)

    tex_blob = collect_tex_sources(latex_dir) if latex_dir.is_dir() else ""
    if not (latex_dir / "main.tex").is_file():
        report.errors.append("latex:missing_main.tex")

    for g in verify_graphics_resolve(root, latex_dir, tex_blob):
        report.errors.append(g)

    bib_path = latex_dir / "references.bib"
    if bib_path.is_file():
        bib_text = bib_path.read_text(encoding="utf-8", errors="replace")
        bib_keys = parse_bib_keys(bib_text)
        cite_keys = extract_cite_keys_from_tex(tex_blob)
        report.checks["bib_entry_count"] = len(bib_keys)
        report.checks["unique_cite_keys_in_tex"] = len(cite_keys)
        missing_bib = sorted(cite_keys - bib_keys)
        orphan_bib = sorted(bib_keys - cite_keys)
        if re.search(r"\\nocite\{\*\}", tex_blob):
            orphan_bib = []
        report.checks["citations_missing_bib_entry"] = missing_bib
        report.checks["bib_entries_never_cited"] = orphan_bib
        for k in missing_bib:
            report.errors.append(f"bib:cite_key_missing_in_bib:{k}")
        for k in orphan_bib:
            report.errors.append(f"bib:uncited_bib_entry:{k}")
    else:
        report.errors.append("bib:missing_references.bib")

    main_tex = (latex_dir / "main.tex").read_text(encoding="utf-8", errors="replace") if (
        latex_dir / "main.tex"
    ).is_file() else ""
    showcase_tex = latex_dir / "chapters" / "m3_fr9_showcase.tex"
    report.errors.extend(fr9_source_checks(tex_blob, showcase_file_exists=showcase_tex.is_file()))
    report.errors.extend(front_matter_list_checks(main_tex))
    for s in main_tex_structure_checks(main_tex):
        report.errors.append(s)

    apply_journal_log_pdf_checks(
        report,
        build_dir=build_dir,
        resolved_prefix=resolved_prefix,
        allow_missing_pdf=allow_missing_pdf,
        skip_page_count=skip_page_count,
        page_min=page_min,
        page_max=page_max,
    )

    report.warnings.extend(bidi_heuristic(tex_blob, content_dir))
    report.checks["bidi_automation"] = "heuristics_only_visual_qa_manual"

    secret_hits = scan_build_for_secrets(build_dir)
    if secret_hits:
        report.errors.extend(secret_hits)
    report.checks["secret_scan_hits"] = len(secret_hits)

    report.passed = len(report.errors) == 0
    (build_dir / "m6_qa_report.json").write_text(
        json.dumps(report.to_json_dict(), indent=2), encoding="utf-8"
    )
    (build_dir / "m6_qa_report.md").write_text(report.to_markdown(), encoding="utf-8")
    return report
