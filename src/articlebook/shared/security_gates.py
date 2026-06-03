"""M8 human gates: paid LLM confirmation and overwrite acknowledgement (CLI)."""

from __future__ import annotations

import sys
from pathlib import Path


def _is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def ensure_paid_llm_confirmed(*, assume_yes: bool) -> None:
    """Block paid LLM runs until the operator types ``yes``, unless ``assume_yes``."""
    if assume_yes:
        return
    if not _is_interactive():
        raise SystemExit(
            "Refusing paid LLM run in non-interactive mode without --yes. "
            "Pass --yes to confirm API spend."
        )
    print(
        "\n--- Paid LLM run ---\n"
        "This run will call the configured provider and may incur cost.\n"
        "Type the word yes (lowercase) and press Enter to continue, or Ctrl+C to abort.\n"
    )
    if input().strip() != "yes":
        raise SystemExit("Aborted: confirmation not given.")


def _existing_content_latex_artifacts(root: Path) -> list[Path]:
    found: list[Path] = []
    content = root / "content"
    if content.is_dir():
        found.extend(p for p in content.glob("*.md") if p.is_file())
    latex = root / "latex"
    for rel in ("main.tex", "references.bib"):
        p = latex / rel
        if p.is_file():
            found.append(p)
    ch = latex / "chapters"
    if ch.is_dir():
        found.extend(p for p in ch.glob("*.tex") if p.is_file())
    return sorted({p.resolve() for p in found})


def ensure_overwrite_artifacts_confirmed(
    root: Path, *, assume_yes: bool, dry_run: bool
) -> None:
    """Warn before clobbering existing Markdown/LaTeX outputs (unless --yes or dry-run)."""
    if assume_yes or dry_run:
        return
    paths = _existing_content_latex_artifacts(root)
    if not paths:
        return
    if not _is_interactive():
        raise SystemExit(
            "Existing content/latex artifacts detected; refusing to overwrite in "
            "non-interactive mode without --yes. Pass --yes after review, or use --dry-run."
        )
    rels = "\n".join(f"  - {p.relative_to(root)}" for p in paths[:40])
    more = "" if len(paths) <= 40 else f"\n  … and {len(paths) - 40} more"
    print(
        "\n--- Overwrite warning ---\n"
        "The following files already exist and may be overwritten:\n"
        f"{rels}{more}\n\n"
        "Type yes to allow overwrites for this run, or Ctrl+C to abort.\n"
    )
    if input().strip() != "yes":
        raise SystemExit("Aborted: overwrite not confirmed.")
