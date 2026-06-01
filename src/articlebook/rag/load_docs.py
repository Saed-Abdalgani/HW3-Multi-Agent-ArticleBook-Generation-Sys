"""Load local knowledge files (txt/md/pdf) under ``knowledge/`` (M9-OPT)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pypdf import PdfReader

from articlebook.shared.config import load_models_document


def _parse_md_frontmatter(raw: str, fallback_id: str) -> tuple[str, str]:
    if not raw.startswith("---"):
        return fallback_id, raw.strip()
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return fallback_id, raw.strip()
    meta = yaml.safe_load(parts[1]) or {}
    bib = str(meta.get("bib_key", fallback_id))
    return bib, parts[2].strip()


def load_knowledge_records(root: Path) -> list[dict[str, Any]]:
    """Return records ``{source_id, text, path}`` for all supported files."""
    doc = load_models_document()
    rag = doc.get("rag") or {}
    kd = root / str(rag.get("knowledge_dir", "knowledge"))
    if not kd.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(kd.rglob("*")):
        if not path.is_file():
            continue
        suf = path.suffix.casefold()
        try:
            if suf in {".md", ".markdown"}:
                raw = path.read_text(encoding="utf-8", errors="replace")
                sid, body = _parse_md_frontmatter(raw, path.stem)
                rel = str(path.relative_to(root))
                rows.append({"source_id": sid, "text": body, "path": rel})
            elif suf == ".txt":
                body = path.read_text(encoding="utf-8", errors="replace").strip()
                rel = str(path.relative_to(root))
                rows.append({"source_id": path.stem, "text": body, "path": rel})
            elif suf == ".pdf":
                reader = PdfReader(str(path))
                parts = []
                for page in reader.pages:
                    parts.append(page.extract_text() or "")
                body = "\n".join(parts).strip()
                rel = str(path.relative_to(root))
                rows.append({"source_id": path.stem, "text": body, "path": rel})
        except OSError:
            continue
    return rows
