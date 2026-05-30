---
name: bidi-hebrew
description: RTL Hebrew authoring with safe LTR islands for English, numerals, and code in Markdown destined for LuaLaTeX BiDi.
metadata:
  author: articlebook
  version: "1.0"
---

# BiDi Hebrew (Markdown stage)

- Assume **RTL base** when the run language is Hebrew; keep English technical tokens in **LTR islands** using explicit markers described by the LaTeX builder in M4 (`\\LR{...}` in TeX—here, wrap inline English in backticks or `<span dir="ltr">...</span>` notes the converter must honor).
- **Never** mix bare Latin digits inside Hebrew sentences without isolation—use `123` inside backticks for code-like spans when ambiguous.
- Watch **punctuation mirroring**; prefer explicit parentheses content in English inside backticks.
- Provide at least one **mixed-direction** sample paragraph in drafts when Hebrew is selected.
