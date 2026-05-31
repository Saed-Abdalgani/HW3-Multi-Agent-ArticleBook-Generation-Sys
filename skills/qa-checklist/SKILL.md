---
name: qa-checklist
description: Technical contract checklist for links, citations, BiDi, required FR-9 elements, and compilation diagnostics before declaring a build READY.
metadata:
  author: articlebook
  version: "1.1"
---

# QA checklist (M1 placeholders → M6 contract)

1. **Artifacts exist** on disk for each stage (research, outline, writing, figures, TeX, compile log, QA report).
2. **Compilation log** under `build/`; classify `! LaTeX Error` vs warnings; scan for undefined cites/refs.
3. **Figures path probe:** every `\includegraphics` target resolves relative to `latex/`.
4. **Secrets:** no API keys in logs or `build/*.{log,json}`.
5. **M6 (FR-20):** call the **`run_m6_contract_checks`** tool after canonical compile; it writes `build/m6_qa_report.md` with bib↔cite consistency, FR-9, page count (15–20), and structure checks.
6. **BiDi (FR-13):** after automation passes, visually confirm RTL↔LTR in the PDF BiDi chapter.
