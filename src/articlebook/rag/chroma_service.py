"""Chroma persistent index + query for M9-OPT (lazy imports)."""

from __future__ import annotations

import gc
import json
import logging
from pathlib import Path
from typing import Any

from articlebook.rag.chunk_text import chunk_text
from articlebook.rag.load_docs import load_knowledge_records
from articlebook.shared.config import load_models_document

log = logging.getLogger(__name__)


def _persist_path(root: Path) -> Path:
    doc = load_models_document()
    sub = str((doc.get("rag") or {}).get("persist_subdir", "rag_chroma"))
    return root / "build" / sub


def _rag_ints(root: Path) -> tuple[int, int, int]:
    r = (load_models_document().get("rag") or {})
    return (
        int(r.get("chunk_size", 480)),
        int(r.get("chunk_overlap", 80)),
        int(r.get("top_k", 5)),
    )


def rebuild_chroma_index(root: Path) -> int:
    """Refresh the Chroma collection in-place (avoids Windows file locks on sqlite)."""
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    gc.collect()
    chunk_size, overlap, _top_k = _rag_ints(root)
    persist = _persist_path(root)
    persist.mkdir(parents=True, exist_ok=True)
    ef = DefaultEmbeddingFunction()
    client = chromadb.PersistentClient(path=str(persist))
    col = client.get_or_create_collection("articlebook_rag", embedding_function=ef)
    try:
        prev = col.get()
        pids = prev.get("ids") or []
        if pids:
            col.delete(ids=pids)
    except Exception:
        pass
    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict[str, Any]] = []
    n = 0
    for rec in load_knowledge_records(root):
        sid = rec["source_id"]
        for i, ch in enumerate(chunk_text(rec["text"], chunk_size=chunk_size, overlap=overlap)):
            if not ch.strip():
                continue
            ids.append(f"{sid}:{i}")
            docs.append(ch)
            metas.append({"bib_key": sid, "path": rec["path"]})
            n += 1
    if ids:
        col.add(ids=ids, documents=docs, metadatas=metas)
    log.info("rag.index rebuilt chunks=%s persist=%s", n, persist)
    del col, client
    gc.collect()
    return n


def query_chroma(root: Path, query: str) -> list[dict[str, Any]]:
    """Return top-k snippets with distances and bib keys."""
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    _cs, _ov, top_k = _rag_ints(root)
    persist = _persist_path(root)
    persist.mkdir(parents=True, exist_ok=True)
    ef = DefaultEmbeddingFunction()

    def _open() -> tuple[Any, Any]:
        cl = chromadb.PersistentClient(path=str(persist))
        c = cl.get_or_create_collection("articlebook_rag", embedding_function=ef)
        return cl, c

    client, col = _open()
    try:
        need_build = col.count() == 0
    except Exception:
        need_build = True
    del col
    del client
    gc.collect()
    if need_build:
        rebuild_chroma_index(root)
    client, col = _open()
    try:
        final_cnt = col.count()
    except Exception:
        return []
    if final_cnt == 0:
        return []
    n = min(top_k, max(1, final_cnt))
    res = col.query(query_texts=[query], n_results=n)
    out: list[dict[str, Any]] = []
    ids = (res.get("ids") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    for i in range(len(ids)):
        meta = metas[i] or {}
        out.append(
            {
                "text": docs[i],
                "source_id": str(meta.get("bib_key", "unknown")),
                "distance": float(dists[i]) if dists else 0.0,
                "path": meta.get("path", ""),
            }
        )
    return out


def query_as_json(root: Path, query: str) -> str:
    """JSON string: snippets + empty claims list for downstream Writer / .bib wiring."""
    snippets = query_chroma(root, query)
    payload = {"snippets": snippets, "claims": []}
    return json.dumps(payload, ensure_ascii=False)
