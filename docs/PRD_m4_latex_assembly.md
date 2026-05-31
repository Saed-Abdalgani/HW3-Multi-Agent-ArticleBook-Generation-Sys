# PRD — Milestone M4 (LaTeX assembly)

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Implemented (library + stub + LLM crew) |
| Related | `plan.md` Phase M4; `todo.md` §M4; FR-4, FR-6, FR-8, FR-12–FR-16 |

---

## 1. Purpose

Produce a **single compilable** `latex/main.tex` that:

- Includes all `content/chapter_*.md` as generated `latex/chapters/chapter_*.tex`.
- Appends the M3 FR-9 showcase (`latex/chapters/m3_fr9_showcase.tex`).
- Declares **polyglossia** (English main + Hebrew other), **biblatex+biber**, **hyperref**, **cleveref**, **fancyhdr**, and a **thematic title page** with topic, author, date, and language.
- Runs **one** LuaLaTeX pass (M5 adds biber + extra passes).

---

## 2. Library API

| Function | Role |
|----------|------|
| `assemble_latex_project(root, RunInputs)` | Discover `chapter_*.md`, emit `.tex`, write `main.tex`. |
| `write_m4_stub_manifest(...)` | Stub observability under `build/m4_stub_manifest.md`. |

Implementation: `articlebook.m4_assembly`.

---

## 3. Markdown → TeX (minimal dialect)

- `#` / `##` → `\chapter` / `\section` + `\label{ch:...}`.
- `[@key]` / `[@a; @b]` → `\parencite{key}` / `\parencite{a,b}`.
- `` `code` `` → `\texttt{...}`; `**bold**` → `\textbf{...}`.
- `>` blockquotes → `quote`.
- Full tables / raw LaTeX math in Markdown are **not** parsed (M4 stub content is prose-heavy; M3 math lives in `.tex`).

---

## 4. Tooling (CrewAI)

`assemble_latex_document(topic, language)` — validates inputs, runs `assemble_latex_project`.

`run_lualatex_once(reason, log_filename="...")` — optional log name for M4 (`m4_lualatex_once.log`).

---

## 5. Exit criteria (plan.md)

- **Met:** Assembled project is written and **one** `lualatex` invocation is attempted; unresolved citations/refs are acceptable until M5.
- **CI:** If `lualatex` is absent, the driver writes `build/m4_lualatex_once.log` with a skip message (same pattern as M1).

---

## 6. Known follow-ups (M5–M6)

- Canonical **biber** + multi-pass engine sequence.
- Hebrew **main** document language vs English-main + `hebrew` other (current default for compile stability).
- Richer Markdown (tables, display math) preserved through conversion (R-8).
