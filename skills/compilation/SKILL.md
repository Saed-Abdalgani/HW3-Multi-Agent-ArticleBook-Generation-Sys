---
name: compilation
description: >-
  Canonical LuaLaTeX/XeLaTeX multipass compile with biber between passes, rerun loop,
  log/journal artifacts, and how to interpret failure classes for QA.
metadata:
  author: articlebook
  version: "1.0"
---

# Compilation operator skill

## Canonical pass sequence (plan.md §4)

1. **Engine** — `lualatex -interaction=nonstopmode -halt-on-error main.tex` (or `xelatex` when `ARTICLEBOOK_LATEX_ENGINE=xelatex`), cwd = `latex/`, outputs redirected under `build/`.
2. **Bibliography** — `biber build/main` (or `bibtex`) after the first engine pass produces `.bcf`/`.aux`.
3. **Engine ×2–4** — repeat until rerun/citation warnings stabilize or a safe max pass count is hit.

Always prefer the **`run_latex_canonical_compile`** tool (multipass + journal). Use **`run_lualatex_once`** only for a deliberate smoke pass.

## Artifacts you must preserve

- Per-pass logs: `build/<prefix>_pass*.log`
- **Compile journal** JSON: `build/<prefix>_compile_journal.json` (QA/M6 consumes this; do not delete).
- Optional excerpts: `*_failure.txt`, `*_biber_warning_excerpt.txt`

## Failure triage (FR-19)

Classify using log tails + journal `ok` flag:

| Symptom | Likely class |
|--------|----------------|
| Missing `.sty` / undefined control sequence early | Missing package / bad preamble |
| `! LaTeX Error: File ... not found` for graphics | Broken `figures/` path |
| Undefined citations / empty bibliography | biber not run or `.bib` key mismatch |
| `??` in log after max passes | Need more passes or broken `\\label`/`\\ref` |

Report verbatim tool stderr; never claim success if the PDF or journal indicates failure.
