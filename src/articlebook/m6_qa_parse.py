"""M6: parse LaTeX / BibTeX sources and scan compile logs (subset for QA contract)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_CITE_CMD = re.compile(
    r"\\(?:parencite|cite|textcite|autocite|footcite|nocite|parencites|Cite|Parencite)"
    r"(?:\[[^\]]*\])?\{([^}]+)\}"
)
_BIB_ENTRY_KEY = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")
_UNDEFINED_CITE = re.compile(r"citation.*undefined|undefined citation", re.IGNORECASE)
_UNDEFINED_REF = re.compile(r"reference.*undefined|undefined reference", re.IGNORECASE)
RERUN_OR_UNDEFINED_SUMMARY = re.compile(
    r"There were undefined references|There were undefined citations|Rerun to get",
    re.IGNORECASE,
)


def collect_tex_sources(latex_dir: Path) -> str:
    parts: list[str] = []
    main = latex_dir / "main.tex"
    if main.is_file():
        parts.append(main.read_text(encoding="utf-8", errors="replace"))
    ch = latex_dir / "chapters"
    if ch.is_dir():
        for p in sorted(ch.glob("*.tex")):
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def extract_cite_keys_from_tex(tex_blob: str) -> set[str]:
    keys: set[str] = set()
    for m in _CITE_CMD.finditer(tex_blob):
        inner = m.group(1).strip()
        if inner == "*":
            continue
        for piece in inner.split(","):
            k = piece.strip()
            if k:
                keys.add(k)
    return keys


def parse_bib_keys(bib_text: str) -> set[str]:
    return {m.group(1).strip() for m in _BIB_ENTRY_KEY.finditer(bib_text)}


def collect_includegraphics_paths(tex_blob: str) -> list[str]:
    pat = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
    return pat.findall(tex_blob)


def verify_graphics_resolve(root: Path, latex_dir: Path, tex_blob: str) -> list[str]:
    issues: list[str] = []
    for raw in collect_includegraphics_paths(tex_blob):
        target = (latex_dir / raw).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            issues.append(f"graphics_traversal:{raw}")
            continue
        if not target.is_file():
            issues.append(f"graphics_missing:{raw}")
        elif target.stat().st_size == 0:
            issues.append(f"graphics_empty:{raw}")
    return issues


def scan_log_for_link_citation_issues(log_text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    for line in log_text.splitlines():
        if _UNDEFINED_CITE.search(line) or _UNDEFINED_REF.search(line):
            errors.append(line.strip()[:500])
        elif "??" in line and "warning" in line.lower():
            warns.append(line.strip()[:500])
    if re.search(r"There were undefined references", log_text, re.I):
        errors.append("Log summary: There were undefined references")
    if re.search(r"There were undefined citations", log_text, re.I):
        errors.append("Log summary: There were undefined citations")
    return (errors[:50], warns[:30])


def read_compile_journal(build_dir: Path, log_prefix: str) -> dict[str, Any] | None:
    p = build_dir / f"{log_prefix}_compile_journal.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def resolve_compile_log_prefix(build_dir: Path, hint: str | None) -> str | None:
    if hint and (build_dir / f"{hint}_compile_journal.json").is_file():
        return hint
    if hint:
        return hint
    for prefix in ("m6_crew", "m5_crew", "m5", "m4"):
        if (build_dir / f"{prefix}_compile_journal.json").is_file():
            return prefix
    return None
