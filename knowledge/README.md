# Local knowledge corpus (M9-OPT RAG)

Place **`.md`**, **`.txt`**, or **`.pdf`** files here. They are indexed when `config/models.yaml`
sets `rag.enabled: true` and optional deps are installed (`uv sync --extra rag`).

## BibTeX mapping (`.md` only)

Start Markdown files with YAML front matter so retriever `source_id` matches a `.bib` key:

```yaml
---
bib_key: knuth1984texbook
---

Your notes…
```

If `bib_key` is omitted, the file **stem** (filename without extension) is used as `source_id`.
