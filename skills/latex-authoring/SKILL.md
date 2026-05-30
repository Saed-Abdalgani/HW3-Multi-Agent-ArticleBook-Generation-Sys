---
name: latex-authoring
description: LaTeX structure, preamble packages, Markdown→TeX mapping, and forbidding plain-text mathematics.
metadata:
  author: articlebook
  version: "1.0"
---

# LaTeX authoring

- Target **LuaLaTeX** with `fontspec`, `polyglossia`/`babel`, `graphicx`, `hyperref`, `cleveref`, `fancyhdr`, `amsmath`, `mathtools`, `booktabs`, and bibliography via **biber** (see `plan.md` §4).
- **Math rule:** every displayed expression lives in `equation`, `align`, or `gather`—never a bare `$...$` wall in body copy for complex forms.
- **Labels:** `\label{sec:...}`, `\label{fig:...}`, `\label{tab:...}`, `\label{eq:...}`; reference with `\cref{...}`.
- **Markdown→TeX:** preserve anchors from the Writer; map `<!-- FIG:... -->` to `\input{...}` or `\includegraphics` stubs under `figures/`.
