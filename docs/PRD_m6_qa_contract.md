# PRD — M6 QA contract (FR-20, prd.md §9)

| Field | Value |
|-------|-------|
| Mechanism | Deterministic Python QA (`articlebook.m6_qa`) |
| Entry | `run_m6_contract_qa`, CrewAI tool `run_m6_contract_checks`, CLI `--milestone m6` |
| Related | `plan.md` Phase 6, `todo.md` Phase M6 |

## 1. Purpose

Provide a **repeatable technical contract** after the canonical compile (M5): citations,
cross-references (via log scan), FR-9 assets, document shell (cover, TOC, LOF/LOT,
bibliography driver), PDF page band (15–20), and hygiene (secret patterns in `build/`).

BiDi **visual** correctness (RTL↔LTR) remains a **manual** reviewer step; automation only
checks that Hebrew is declared in `main.tex` and that the BiDi chapter source exists.

## 2. Inputs

- Project root (workspace): `content/`, `latex/`, `figures/`, `build/`.
- Optional `log_prefix` to locate `build/{prefix}_compile_journal.json` (defaults: try
  `m6_crew`, `m5_crew`, `m5`, `m4`).

## 3. Checks (normative)

| ID | Rule | Severity |
|----|------|----------|
| Q1 | M3 figure binaries + `\\includegraphics` targets resolve | Error |
| Q2 | Every `\\cite` / `\\parencite` / … key exists in `references.bib` | Error |
| Q3 | Every `.bib` entry is cited in aggregated `.tex` (unless `\\nocite{*}`) | Error |
| Q4 | FR-9 LaTeX patterns: TikZ, graphics, tabular, `equation`/`align` | Error |
| Q5 | `main.tex` contains title page, TOC, fancyhdr, hyperref, polyglossia, Hebrew, bib print | Error |
| Q6 | Compile journal `ok` is true | Error |
| Q7 | `main.log` has no undefined citation/reference lines | Error |
| Q8 | PDF exists; page count in [15, 20] via `pypdf` | Error |
| Q9 | Optional PDF text `??` heuristic | Warning |
| Q10 | No API-key-like patterns in `build/*.log` and `build/*.json` | Error |
| Q11 | BiDi chapter file + LTR island heuristics | Warning |

## 4. Offline / CI mode

`--m6-allow-missing-pdf` (CLI): when LuaLaTeX is not installed, the driver records
`error_class: missing_engine`. With this flag, M6 **downgrades** missing PDF, missing-engine
journal failure, and **skips** parsing a stale `main.log` so static checks (bib, FR-9,
structure) still run. This is **not** a substitute for a full MiKTeX sign-off.

## 5. Outputs

- `build/m6_qa_report.md` — human-readable summary.
- `build/m6_qa_report.json` — machine-readable payload (`passed`, `errors`, `warnings`, `checks`).

## 6. Exit criteria

Milestone M6 is satisfied when `passed == true` **without** `--m6-allow-missing-pdf` on a
machine with MiKTeX, producing a PDF in the 15–20 page band and clean logs per Q6–Q8.
