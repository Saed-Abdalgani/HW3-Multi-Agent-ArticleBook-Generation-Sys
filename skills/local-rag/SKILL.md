---
name: local-rag
description: >
  Optional local retrieval (M9-OPT / ADR-003): use retrieve_knowledge_snippets when present
  to ground notes in files under knowledge/; map source_id to existing .bib keys.
metadata:
  author: articlebook
  version: "1.0"
---

# Local RAG (optional)

- **When:** Only when the `retrieve_knowledge_snippets` tool is available (requires
  `rag.enabled: true` in `config/models.yaml` and `uv sync --extra rag` for the Chroma client).
- **How:** Call the tool with a short natural-language query; parse the JSON response.
  Each snippet includes `text`, `source_id` (BibTeX key or file stem), and `distance`.
- **Citations:** Prefer `[@source_id]` markers that already exist or will exist in
  `latex/references.bib` so M6 `.bib`↔in-text checks pass.
- **Output shape:** The tool returns `{"snippets":[...], "claims":[]}`. Writers may fill
  `claims` with `{ "claim": "...", "source_id": "..." }` objects in downstream tasks.
