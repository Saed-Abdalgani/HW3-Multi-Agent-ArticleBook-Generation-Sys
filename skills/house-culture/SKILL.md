---
name: house-culture
description: Shared tone and safety rules for every agent in the book-generation crew. Use for citation honesty, artifact hygiene, and never logging secrets.
metadata:
  author: articlebook
  version: "1.0"
---

# House culture (crew-wide)

- Write **machine-reviewable** artifacts (Markdown or `.tex` snippets) under `content/`, `latex/`, `figures/`, `build/`, or `scripts/` using the provided workspace tools.
- Prefer **short, structured** outputs in tasks; defer deep prose to later milestones.
- **Never** invent API keys, file paths outside the sandbox, or fake compilation success—report tool errors verbatim.
- When unsure, **read** `prd.md` / `plan.md` excerpts via `read_workspace_file` instead of guessing requirements.
