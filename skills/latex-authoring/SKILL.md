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
- **M6 PDF contract (must survive into the final build):** at least one **`amsmath`** display environment (`equation`, `align`, or `gather` with real structure—not only inline `$...$` as the sole math), one **`booktabs`** table, one **`\includegraphics`** figure, and one **vector or raster plot** (e.g. Matplotlib output under `figures/`).
