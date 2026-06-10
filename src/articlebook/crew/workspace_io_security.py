"""Guarded workspace read/write (M8): dry-run, overwrite policy, untrusted file reads."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from articlebook.crew.workspace_sandbox import (
    _ensure_under_root,
    _root,
    _validate_relative,
    _validate_relative_read,
)
from articlebook.shared.security import (
    UNTRUSTED_FILE_READ_NOTICE,
    allow_workspace_overwrites_active,
    dry_run_active,
    guard_file_read_payload,
)
from articlebook.shared.security_heuristics import tool_facing_string_has_denylisted_patterns

logger = logging.getLogger(__name__)

# Crew tools must not overwrite LaTeX/biber outputs under ``build/`` (agents have mistaken
# ``build/main.bbl`` for a hand-editable bib file and replaced ``build/main.tex``, nuking PDFs).
_BUILD_COMPILER_SUFFIXES: tuple[str, ...] = (
    ".tex",
    ".pdf",
    ".bbl",
    ".bcf",
    ".aux",
    ".blg",
    ".out",
    ".toc",
    ".lof",
    ".lot",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".xdv",
    ".4tc",
    ".4ct",
    ".idv",
    ".lg",
)


def _forbidden_agent_build_compiler_path(rel: Path) -> str | None:
    """Return a user-facing refusal reason if this path must not be written by tools."""
    parts = rel.parts
    if len(parts) < 2 or parts[0] != "build":
        return None
    name_lower = rel.name.lower()
    if name_lower.startswith("main."):
        return (
            f"Refusing to write {rel.as_posix()}: LaTeX/biber outputs named main.* under "
            "build/ are produced only by run_latex_canonical_compile / run_lualatex_once. "
            "Edit sources under latex/ (e.g. latex/main.tex, latex/references.bib), then re-run compile."
        )
    for suf in _BUILD_COMPILER_SUFFIXES:
        if name_lower.endswith(suf):
            return (
                f"Refusing to write {rel.as_posix()}: under build/, only QA/manifest-style "
                f"artifacts (e.g. *.md, *.json reports) may be written by tools — not {suf} files."
            )
    if name_lower.endswith(".synctex.gz"):
        return f"Refusing to write {rel.as_posix()}: synctex bundles are compiler-owned."
    return None


def _write_needs_explicit_overwrite(rel: Path) -> bool:
    s = rel.as_posix()
    return not s.startswith("build/")


def guarded_write_workspace_file(relative_path: str, content: str) -> str:
    """Write UTF-8 text with M8 dry-run and overwrite controls."""
    root = _root()
    rel = _validate_relative(relative_path)
    reason = _forbidden_agent_build_compiler_path(rel)
    if reason:
        raise ValueError(reason)
    deny = tool_facing_string_has_denylisted_patterns(content)
    if deny:
        raise ValueError(
            "write_workspace_file: content matches denylisted patterns: " + ", ".join(deny)
        )
    dest = _ensure_under_root(root, rel)
    if dry_run_active():
        exists = " (would overwrite existing)" if dest.is_file() else ""
        return (
            f"DRY-RUN: would write {dest.relative_to(root)}{exists} "
            f"({len(content)} chars). No bytes written."
        )
    if (
        dest.is_file()
        and _write_needs_explicit_overwrite(rel)
        and not allow_workspace_overwrites_active()
    ):
        raise ValueError(
            f"Refusing to overwrite {dest.relative_to(root)} without operator approval. "
            "Re-run with --yes after reviewing existing artifacts, or delete the file first."
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    msg = f"Wrote {dest.relative_to(root)} ({len(content)} chars)."
    logger.info(
        "artifact.write path=%s bytes=%s",
        dest.relative_to(root),
        len(content.encode("utf-8")),
    )
    return msg


def guarded_write_workspace_files_batch(files_json: str) -> str:
    """Write many files from one JSON array of ``{\"relative_path\": \"...\", \"content\": \"...\"}``.

    Crew models often emit a JSON list when asked to update several paths; the single-file
    ``write_workspace_file`` tool rejects that shape. This entry point accepts the list and
    delegates each row to ``guarded_write_workspace_file`` (same denylist / dry-run / overwrite
    rules apply per file).
    """
    raw = (files_json or "").strip()
    if not raw:
        raise ValueError("write_workspace_files_batch: empty JSON payload")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"write_workspace_files_batch: invalid JSON: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("write_workspace_files_batch: top-level JSON must be an array")
    if len(data) > 24:
        raise ValueError("write_workspace_files_batch: at most 24 file objects per call")
    lines: list[str] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"write_workspace_files_batch: item {i} must be a JSON object")
        rel = item.get("relative_path")
        content = item.get("content")
        if not isinstance(rel, str) or not isinstance(content, str):
            raise ValueError(
                f"write_workspace_files_batch: item {i} needs string fields "
                '"relative_path" and "content"'
            )
        lines.append(guarded_write_workspace_file(rel, content))
    return "\n".join(lines)


def guarded_read_workspace_file(relative_path: str) -> str:
    """Read UTF-8 text with traversal checks and M8 read hardening."""
    root = _root()
    rel = _validate_relative_read(relative_path)
    src = (root / rel).resolve()
    if not src.is_relative_to(root.resolve()):
        raise ValueError("Invalid read target.")
    if not src.is_file():
        return f"Missing file: {src.relative_to(root)}"
    text = src.read_text(encoding="utf-8")
    rel_pos = rel.as_posix()
    safe = guard_file_read_payload(text, relative_path=rel_pos)
    logger.info("artifact.read path=%s chars=%s", src.relative_to(root), len(text))
    return f"{safe}\n\n{UNTRUSTED_FILE_READ_NOTICE}"
