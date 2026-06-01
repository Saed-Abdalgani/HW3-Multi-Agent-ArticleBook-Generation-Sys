# PRD — M9-OPT optional local RAG (ADR-003)

Implements `plan.md` §10.6 and `todo.md` Phase M9-OPT: **off by default**, local file-backed
retrieval for the Research agent.

## Configuration

- `config/models.yaml` → `rag.enabled` (default `false`).
- Environment override: `ARTICLEBOOK_RAG_ENABLED=true`.
- Optional Python extras: `uv sync --extra rag` (installs **Chroma**; embeddings use Chroma’s default ONNX MiniLM — no PyTorch stack).

## Layout

| Path | Role |
|------|------|
| `knowledge/` | Corpus (`.md` with optional `bib_key` front matter, `.txt`, `.pdf`) |
| `build/<rag.persist_subdir>/` | Chroma persistent store (default `build/rag_chroma`) |

## Crew integration

- Tool: `retrieve_knowledge_snippets` (Research agent only when flag + deps allow).
- JSON payload: `snippets[]` with `source_id` suitable for `[@source_id]` and M6 checks.
- Skill: `skills/local-rag/SKILL.md`.

## Exit criteria (M9-OPT)

Retriever returns cited snippets with `source_id` aligned to `.bib` keys when front matter
or filenames are chosen accordingly; M6 consistency passes when those keys exist in
`latex/references.bib`.
