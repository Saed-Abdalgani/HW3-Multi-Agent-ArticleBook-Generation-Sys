"""M9-OPT RAG: chunking, flags, and optional Chroma round-trip."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from articlebook.rag.chunk_text import chunk_text
from articlebook.rag.deps import rag_stack_importable
from articlebook.rag.load_docs import load_knowledge_records
from articlebook.shared.config import load_models_document, rag_feature_enabled


def test_chunk_text_overlap() -> None:
    t = "abcdefghijklmnopqrstuvwxyz"
    parts = chunk_text(t, chunk_size=10, overlap=4)
    assert len(parts) >= 2
    assert "".join(parts[:1])[0] == "a"


def test_rag_feature_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "models.yaml").write_text("version: '1'\nrag:\n  enabled: false\n", encoding="utf-8")
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg))
    monkeypatch.setenv("ARTICLEBOOK_RAG_ENABLED", "true")
    assert rag_feature_enabled() is True


def test_load_knowledge_records_reads_frontmatter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kd = tmp_path / "knowledge"
    kd.mkdir()
    (kd / "x.md").write_text("---\nbib_key: mykey\n---\nbody text", encoding="utf-8")
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "models.yaml").write_text(
        "version: '1'\nrag:\n  enabled: false\n  knowledge_dir: knowledge\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg))
    rows = load_knowledge_records(tmp_path)
    assert any(r["source_id"] == "mykey" and "body text" in r["text"] for r in rows)


@pytest.mark.skipif(not rag_stack_importable(), reason="optional [rag] extra not installed")
def test_chroma_query_returns_snippets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    kd = tmp_path / "knowledge"
    kd.mkdir()
    (kd / "doc.md").write_text(
        "---\nbib_key: citekey\n---\nUniqueRagPhraseAlphaOmega",
        encoding="utf-8",
    )
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "models.yaml").write_text(
        "version: '1'\nrag:\n  enabled: true\n  knowledge_dir: knowledge\n"
        "  chunk_size: 80\n  chunk_overlap: 10\n  top_k: 2\n  persist_subdir: rag_test\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg))
    from articlebook.rag.chroma_service import query_as_json

    out = json.loads(query_as_json(tmp_path, "UniqueRagPhraseAlphaOmega"))
    assert out["claims"] == []
    assert any(s.get("source_id") == "citekey" for s in out["snippets"])


def test_models_default_includes_rag_keys() -> None:
    doc = load_models_document()
    assert "enabled" in (doc.get("rag") or {})
