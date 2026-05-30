# Implementation Backlog (TODO)

## Multi-Agent Article/Book Generation System with CrewAI and LaTeX

| Field | Value |
|-------|-------|
| Document version | 1.0 |
| Status | Active backlog |
| Author | Senior Software Engineer |
| Last updated | 2026-05-30 |
| Related documents | `prd.md` (PRD), `plan.md` (Implementation Plan) |

---

## How to Use This Backlog

This file decomposes the seven milestones (M0–M6) from `plan.md` into granular, actionable
tasks. Tasks are written so each can be picked up, executed, and verified independently.
Check items off as they are completed.

### Legend

**Priority labels**
- `[P0]` — Blocker / critical path. Must be done for the pipeline to function.
- `[P1]` — High. Required for a requirement-compliant deliverable.
- `[P2]` — Medium. Quality, hardening, or maintainability improvements.
- `[P3]` — Low. Nice-to-have / future enhancement.

**Tags**
- `(FR-n)` — Maps the task to a Functional Requirement in `prd.md`.
- `(NFR-n)` — Maps the task to a Non-Functional Requirement in `prd.md`.
- `(R-n)` — Addresses a risk from `plan.md` §6.
- `(US-n)` — Supports a User Story in `prd.md`.
- `> Note:` — Technical guidance, gotchas, or acceptance hints.

### Status conventions
- `- [ ]` Not started
- `- [x]` Complete
- Use a strikethrough or `(cancelled)` suffix for dropped tasks.

---

## Requirement Traceability Quick Reference

Use this table to confirm every required document element has at least one owning task.

| Requirement | PRD ID | Owning Phase | Primary Task Anchor |
|-------------|--------|--------------|---------------------|
| CrewAI agent crew | FR-1 | M1 | §M1.2 |
| Skills injection (per-agent/crew/programmatic) | FR-2, FR-3 | M1 | §M1.1, §M1.3 |
| Dedicated LaTeX-generation agent | FR-4 | M1, M4 | §M1.2, §M4.1 |
| Topic + language input | FR-5 | M0, M2 | §M0.4, §M2.1 |
| Markdown-first authoring | FR-6 | M2 | §M2.3 |
| 15–20 page length | FR-7 | M2, M6 | §M2.2, §M6.4 |
| TOC, chapters, headers/footers | FR-8 | M4 | §M4.2, §M4.3 |
| Diagram | FR-9 | M3 | §M3.1 |
| Image | FR-9 | M3 | §M3.2 |
| Python-generated graph | FR-9 | M3 | §M3.3 |
| Table | FR-9 | M3 | §M3.4 |
| Decorated mathematical formula | FR-9, FR-10 | M3 | §M3.5 |
| Correct figure paths | FR-11 | M3, M4 | §M3.6 |
| Thematic cover page | FR-12 | M4 | §M4.2 |
| BiDi chapter (RTL↔LTR) | FR-13 | M2, M4 | §M2.5, §M4.4 |
| Full RTL layout for Hebrew | FR-14 | M4 | §M4.4 |
| `.bib` + BibTeX/biber | FR-15 | M2, M5 | §M2.4, §M5.2 |
| Linked bibliography + citations | FR-16 | M5, M6 | §M5.3, §M6.2 |
| MiKTeX + LuaLaTeX/XeLaTeX | FR-17 | M0, M5 | §M0.1, §M5.1 |
| Multi-pass compilation | FR-18 | M5 | §M5.1 |
| Compilation diagnostics | FR-19 | M5, M6 | §M5.4, §M6.5 |
| QA technical contract | FR-20 | M6 | §M6.1–§M6.5 |

---

## Phase M0 — Environment & Scaffolding

> Goal: A reproducible toolchain and a minimal `main.tex` that compiles a cover + TOC
> through the full pass sequence. Exit criteria: "hello world" `.tex` compiles to PDF.

### M0.1 — Toolchain installation & verification
- [ ] `[P0]` Install MiKTeX (current release) and add it to `PATH`. (FR-17, R-6)
- [ ] `[P0]` Verify `lualatex --version` runs from a fresh shell. (FR-17)
- [ ] `[P1]` Verify `xelatex --version` runs as a fallback engine. (FR-17, R-6)
- [ ] `[P0]` Verify `biber --version` and `bibtex --version` are available. (FR-15, R-6)
- [ ] `[P1]` Configure MiKTeX package install to "Yes (ask me first)" or pre-install
  required packages to avoid mid-build prompts. (R-6)
  > Note: Silent on-the-fly installs can hang headless runs; pre-install in CI-like setups.
- [ ] `[P0]` Install Python 3.x and confirm `python --version`. (FR-9)
- [ ] `[P0]` Install Matplotlib in the project environment via the package manager. (FR-9)
  > Note: Use a managed venv/conda env; do not edit requirements files by hand.
- [ ] `[P0]` Install CrewAI and required tool packages via the package manager. (FR-1)
- [ ] `[P2]` Record exact tool versions in a `versions.txt` for reproducibility. (NFR-3)

### M0.2 — Hebrew font & BiDi prerequisites
- [ ] `[P0]` Install a Hebrew-capable Unicode font (e.g., a David/Frank Ruehl class
  OpenType font) and confirm the OS can resolve it. (FR-13, FR-14, R-1)
- [ ] `[P1]` Confirm LuaLaTeX can load the font via `fontspec`. (FR-14, R-1)
- [ ] `[P2]` Document the chosen font name and fallback in `versions.txt`. (NFR-10)

### M0.3 — Project working-directory skeleton
- [ ] `[P0]` Create the working-directory layout from `plan.md` §1.4:
  `content/`, `figures/`, `scripts/`, `latex/chapters/`, `build/`. (NFR-1, NFR-8)
- [ ] `[P1]` Add a `.gitignore` for `build/` artifacts (`*.aux`, `*.log`, `*.pdf`,
  `*.bbl`, `*.bcf`, `*.run.xml`, `*.toc`, `*.out`). (NFR-8)
- [ ] `[P2]` Add a top-level `README` stub describing the run command. (NFR-10)
  > Note: Do not over-document; a short run snippet suffices for handoff.

### M0.4 — Minimal compiling skeleton & run entry point
- [ ] `[P0]` Author a minimal `latex/main.tex` with document class, `fontspec`,
  Hebrew font setup, a cover stub, and `\tableofcontents`. (FR-8, FR-12)
- [ ] `[P0]` Create a CLI/run entry point that accepts `--topic` and `--language`
  arguments. (FR-5, US-1)
  > Note: Language drives RTL vs LTR base direction and font selection downstream.
- [ ] `[P0]` Compile the skeleton through the full pass sequence and confirm a PDF
  is produced in `build/`. (FR-17, FR-18)
- [ ] `[P1]` Capture the compile log and confirm zero errors. (FR-19)

### M0.5 — Secrets & configuration
- [ ] `[P0]` Load LLM API credentials from environment variables / secret storage. (NFR-9)
  > Note: Never hard-code or log secrets; reference them as redacted in any output. (R-10)
- [ ] `[P1]` Add a config file/object for model name, temperature, and seed. (NFR-3)
- [ ] `[P2]` Validate required env vars are present at startup with a clear error. (NFR-5)

### M0 — Exit gate
- [ ] `[P0]` ✅ Milestone M0 sign-off: skeleton compiles to PDF; toolchain verified;
  config and secrets wired. (plan.md M0 exit criteria)

---

## Phase M1 — Skills & Agent Definitions

> Goal: Author all `SKILL.md` packages and define every agent with roles, goals,
> skills, and tools; wire the crew end-to-end on a stub topic.

### M1.1 — Skills scaffolding (file-based packages)
- [ ] `[P0]` Create the `skills/` root and one folder per skill with a required
  `SKILL.md` (YAML front matter + Markdown body). (FR-2, NFR-1)
  > Note: Optional `references/` and `scripts/` subfolders per CrewAI skill anatomy.
- [ ] `[P0]` Author `skills/technical-writing/SKILL.md` (structure, tone, house style).
  (FR-2, US-3)
- [ ] `[P0]` Author `skills/bidi-hebrew/SKILL.md` (RTL rules, LTR islands, term handling).
  (FR-13, R-1)
- [ ] `[P0]` Author `skills/latex-authoring/SKILL.md` (preamble, math, refs, conversion
  rules). (FR-4, R-2, R-8)
- [ ] `[P0]` Author `skills/figure-generation/SKILL.md` (diagram/graph/table conventions,
  path rules). (FR-9, FR-11)
- [ ] `[P0]` Author `skills/qa-checklist/SKILL.md` (the technical contract checklist).
  (FR-20)
- [ ] `[P1]` Author `skills/research-methodology/SKILL.md` (source vetting, `.bib` format).
  (FR-15)
- [ ] `[P1]` Author `skills/document-structure/SKILL.md` (chapter plan, page budgeting).
  (FR-7, FR-8)
- [ ] `[P2]` Validate each `SKILL.md` YAML front matter parses (`name`, `description`,
  `metadata`). (NFR-1)
  > Note: `description` is the agent's selection signal — keep it specific and action-oriented.

### M1.2 — Agent definitions
- [ ] `[P0]` Define the **Research Agent** (role/goal/backstory) with
  `research-methodology` skill and search/file-read tools. (FR-1, FR-2)
- [ ] `[P0]` Define the **Outline/Architect Agent** with `document-structure` skill. (FR-1)
- [ ] `[P0]` Define the **Writer Agent** with `technical-writing` + `bidi-hebrew` skills.
  (FR-1, FR-13)
- [ ] `[P0]` Define the **Figure/Graph Agent** with `figure-generation` skill and a
  Python-execution tool. (FR-1, FR-9)
- [ ] `[P0]` Define the **LaTeX Builder Agent** with `latex-authoring` skill and
  file read/write tools. (FR-4)
- [ ] `[P0]` Define the **Compilation Agent** with a shell/process-execution tool. (FR-17)
- [ ] `[P0]` Define the **QA/Review Agent** with `qa-checklist` skill and log-parsing
  tools. (FR-20)
- [ ] `[P2]` Confirm agent-level skills override crew-level skills where both exist. (FR-3)

### M1.3 — Skill wiring strategies
- [ ] `[P1]` Wire per-agent skills via the `skills=[...]` parameter. (FR-3)
- [ ] `[P2]` Optionally set crew-level default skills for shared "house culture". (FR-3)
- [ ] `[P2]` Implement programmatic loading (`discover_skills` / `activate_skill`) as an
  alternative path and document when to use each. (FR-3, NFR-1)

### M1.4 — Crew assembly & dry run
- [ ] `[P0]` Assemble the Crew with agents + tasks in the correct order
  (research → outline → write → figures → latex → compile → QA). (FR-1)
- [ ] `[P0]` Wire the shared working directory so artifacts pass between stages. (NFR-8)
- [ ] `[P0]` Run the crew on a stub topic; confirm each stage emits a placeholder
  artifact. (US-9)
- [ ] `[P1]` Add structured logging of each stage's inputs/outputs/artifacts. (NFR-8)

### M1 — Exit gate
- [ ] `[P0]` ✅ Milestone M1 sign-off: crew runs end-to-end on a stub producing
  placeholder artifacts. (plan.md M1 exit criteria)

---

## Phase M2 — Content Pipeline

> Goal: Produce a complete, reviewable Markdown draft (15–20 page estimate) with sources,
> including the BiDi chapter. Authoring is Markdown-first.

### M2.1 — Input handling
- [ ] `[P0]` Accept and validate `topic` and `language` inputs from the entry point.
  (FR-5, US-1)
- [ ] `[P1]` Normalize language to a base direction (RTL for Hebrew, LTR otherwise). (FR-14)
- [ ] `[P2]` Echo resolved run configuration to the log for traceability. (NFR-8)

### M2.2 — Outline & page budgeting
- [ ] `[P0]` Generate a chapter/section outline sized for a 15–20 page target. (FR-7, FR-8)
- [ ] `[P1]` Assign a per-chapter page/word budget to control final length. (FR-7, R-5)
  > Note: Track cumulative budget so total stays within 15–20 pages.
- [ ] `[P1]` Reserve one chapter explicitly as the **BiDi demonstration chapter**. (FR-13)
- [ ] `[P2]` Persist the outline to `content/outline.md` for review. (US-2)

### M2.3 — Markdown drafting
- [ ] `[P0]` Draft each chapter as a separate file under `content/`. (FR-6, US-2)
- [ ] `[P1]` Insert placeholders/anchors where figures, tables, and formulas will go.
  (FR-9)
  > Note: Stable anchors let the LaTeX Builder wire assets without restructuring text.
- [ ] `[P1]` Insert in-text citation markers tied to planned `.bib` keys. (FR-16)
- [ ] `[P2]` Provide a human review gate on the Markdown before LaTeX conversion. (R-7, US-2)

### M2.4 — Research & bibliography sourcing
- [ ] `[P0]` Collect credible sources for each chapter via the Research Agent. (FR-15)
- [ ] `[P0]` Build `latex/references.bib` with valid BibTeX entries and stable keys.
  (FR-15, FR-16)
- [ ] `[P1]` Ensure every in-text citation marker has a matching `.bib` entry. (FR-16, R-3)
- [ ] `[P1]` Flag and remove unverifiable/hallucinated sources. (R-7)
  > Note: No orphan citations and no `.bib` entries without an in-text reference.
- [ ] `[P2]` Normalize author/title/year fields for consistent rendering. (NFR-10)

### M2.5 — BiDi chapter content
- [ ] `[P0]` Author the BiDi chapter mixing Hebrew (RTL) with English/technical terms
  (LTR islands). (FR-13, R-1)
- [ ] `[P1]` Verify reading order of mixed runs is logically correct in the source. (FR-13)
- [ ] `[P2]` Include at least one sentence with inline numerals/code to stress BiDi. (R-1)

### M2 — Exit gate
- [ ] `[P0]` ✅ Milestone M2 sign-off: complete reviewable Markdown draft (15–20 page
  estimate) with `.bib` sources. (plan.md M2 exit criteria)

---

## Phase M3 — Figures, Tables & Formulas

> Goal: Generate every required document element (FR-9) and save assets with correct
> relative paths referenced by the source.

### M3.1 — Diagram (FR-9)
- [ ] `[P0]` Decide diagram approach: TikZ (native) or Python-exported vector image. (FR-9)
- [ ] `[P0]` Produce the diagram asset and save to `figures/diagram.pdf` (or inline TikZ).
  (FR-9, FR-11)
- [ ] `[P1]` Add a caption and a `\label{}` for cross-referencing. (FR-16)
  > Note: The diagram is technical (distribution/structure), not narrative content.
- [ ] `[P2]` Confirm the diagram scales without rasterization artifacts. (NFR-2)

### M3.2 — Image (FR-9)
- [ ] `[P0]` Select/produce an image asset and save to `figures/image.png`. (FR-9, FR-11)
- [ ] `[P1]` Add caption + `\label{}`; verify license/attribution if external. (FR-16)
- [ ] `[P2]` Confirm resolution is adequate for print (≥150–300 DPI). (NFR-2)

### M3.3 — Python-generated graph (FR-9)
- [ ] `[P0]` Write `scripts/make_graph.py` using Matplotlib to render a graph. (FR-9)
- [ ] `[P0]` Export the graph to `figures/graph.pdf` (vector preferred). (FR-9, FR-11)
- [ ] `[P1]` Make the script deterministic (fixed seed/data) for reproducibility. (NFR-3)
- [ ] `[P1]` Add caption + `\label{}` and reference it in text. (FR-16)
- [ ] `[P2]` Assert the script exits 0 and the output file is non-empty. (R-4)
  > Note: This satisfies the "graph generated using Python code" requirement explicitly.

### M3.4 — Table (FR-9)
- [ ] `[P0]` Author at least one table (e.g., `tabular`/`booktabs`). (FR-9)
- [ ] `[P0]` Add caption + `\label{}` and ensure it appears in the List of Tables. (FR-8)
- [ ] `[P1]` Verify the table renders correctly under RTL if language is Hebrew. (FR-14, R-1)
  > Note: Table/Figure entries must not break visual marking in the indexes. (FR-20)

### M3.5 — Decorated mathematical formula (FR-9, FR-10)
- [ ] `[P0]` Author at least one non-trivial formula using `amsmath`/`mathtools`. (FR-10)
- [ ] `[P0]` Use a proper math environment (e.g., `equation`/`align`), not plain text.
  (FR-10, R-2)
- [ ] `[P1]` Add a `\label{}` and reference the equation by number in text. (FR-16)
- [ ] `[P1]` Verify the formula renders correctly even within a Hebrew (RTL) paragraph.
  (FR-10, R-1, R-2)
  > Note: A formula written as plain text due to Hebrew–English mixing is NOT accepted.
- [ ] `[P2]` Add at least one decorated element (matrix, cases, fraction, or operator)
  to demonstrate typeset math. (FR-10)

### M3.6 — Asset path integrity (FR-11)
- [ ] `[P0]` Standardize all assets under `figures/` with relative paths. (FR-11, R-4)
- [ ] `[P0]` Confirm each `\includegraphics`/input target resolves from `latex/`. (FR-11)
- [ ] `[P1]` Add a pre-build check listing missing asset files. (R-4, NFR-5)

### M3 — Exit gate
- [ ] `[P0]` ✅ Milestone M3 sign-off: all FR-9 elements exist on disk and resolve in the
  source (diagram, image, Python graph, table, decorated formula). (plan.md M3 exit)

---

## Phase M4 — LaTeX Assembly

> Goal: The LaTeX Builder Agent converts finalized Markdown to `.tex`, wires the preamble,
> cover, TOC, headers/footers, BiDi, and bibliography. Exit: project compiles once.

### M4.1 — Markdown → LaTeX conversion
- [ ] `[P0]` Implement the conversion in the LaTeX Builder Agent (per
  `latex-authoring` skill). (FR-4, FR-6)
- [ ] `[P0]` Map Markdown chapters to `latex/chapters/*.tex` includes. (FR-4, FR-8)
- [ ] `[P1]` Preserve tables, math, and citation markers during conversion. (R-8)
  > Note: Validate converted output against the required-elements checklist (FR-9).
- [ ] `[P2]` Keep generated `.tex` human-readable and lightly commented. (NFR-10)

### M4.2 — Preamble, cover & TOC
- [ ] `[P0]` Finalize `main.tex` document class and core packages. (FR-8)
- [ ] `[P0]` Build the **thematic cover page** with title, author, date, and language.
  (FR-12, US-7)
- [ ] `[P0]` Enable `\tableofcontents` (and List of Figures/Tables as needed). (FR-8)
- [ ] `[P1]` Configure `hyperref` for clickable TOC and citation links. (FR-16)
- [ ] `[P1]` Configure `cleveref` for typed cross-references (Fig./Tab./Eq.). (FR-16)
- [ ] `[P2]` Ensure metadata (PDF title/author) is set via `hyperref`. (NFR-10)

### M4.3 — Headers & footers
- [ ] `[P0]` Configure `fancyhdr` for chapter-aware headers and page-number footers.
  (FR-8)
- [ ] `[P1]` Verify header/footer alignment is correct under RTL for Hebrew. (FR-14, R-1)
- [ ] `[P2]` Confirm front-matter vs main-matter page numbering is consistent. (FR-8)

### M4.4 — BiDi / RTL configuration
- [ ] `[P0]` Configure `polyglossia` (or `babel`) with Hebrew main language + English
  otherlanguage, plus `fontspec` Hebrew font. (FR-13, FR-14, R-1)
  > Note: LuaLaTeX recommended for Hebrew BiDi; XeLaTeX acceptable as fallback.
- [ ] `[P0]` Wrap LTR islands (English/technical terms, numbers, code) appropriately
  in the BiDi chapter. (FR-13, R-1)
- [ ] `[P1]` Verify full RTL layout: TOC, captions, headers, table/figure numbering. (FR-14)
- [ ] `[P1]` Confirm formulas render correctly inside RTL paragraphs. (FR-10, R-2)
- [ ] `[P2]` Add a focused visual snapshot of the BiDi chapter for review. (US-5)

### M4.5 — Bibliography integration
- [ ] `[P0]` Wire `references.bib` via the chosen backend (biblatex+biber or natbib+
  bibtex). (FR-15, FR-16)
- [ ] `[P0]` Add the `\printbibliography`/`\bibliography` call at document end. (FR-16)
- [ ] `[P1]` Confirm in-text `\cite`/`\autocite` keys match `.bib` keys. (FR-16, R-3)

### M4 — Exit gate
- [ ] `[P0]` ✅ Milestone M4 sign-off: assembled project compiles once (placeholders for
  unresolved refs allowed at this stage). (plan.md M4 exit criteria)

---

## Phase M5 — Compilation & Link Resolution

> Goal: Implement the canonical multi-pass compilation and resolve all cross-references
> and citation links. Exit: clean build; all citations/refs clickable and resolving.

### M5.1 — Multi-pass compilation driver
- [ ] `[P0]` Implement a Python subprocess driver for the canonical sequence: (FR-18)
  1. `lualatex main.tex`
  2. `biber main` (or `bibtex main`)
  3. `lualatex main.tex`
  4. `lualatex main.tex`
  5. optional `lualatex main.tex`
- [ ] `[P0]` Run the engine from the correct working directory so `.aux`/`.bcf` land in
  `build/`. (FR-18, R-4)
- [ ] `[P1]` Add an XeLaTeX fallback path selectable by config. (FR-17, R-6)
- [ ] `[P1]` Capture stdout/stderr and exit codes for each pass. (FR-19, NFR-8)
- [ ] `[P2]` Make the driver idempotent and safe to re-run. (NFR-3)

### M5.2 — Bibliography compilation
- [ ] `[P0]` Execute biber/bibtex between the first and subsequent engine passes. (FR-15)
- [ ] `[P1]` Detect and surface biber errors (missing keys, malformed entries). (FR-19, R-3)
- [ ] `[P2]` Confirm `.bbl` is regenerated when `.bib` changes. (NFR-3)

### M5.3 — Reference & citation resolution
- [ ] `[P0]` Loop additional engine passes until no "Rerun to get cross-references
  right" warning remains (cap at a safe maximum). (FR-18, R-3)
- [ ] `[P0]` Confirm zero unresolved `??` markers in the final PDF/log. (FR-16, R-3)
- [ ] `[P1]` Verify every `\cite` resolves and links jump to the bibliography entry.
  (FR-16, US-6)
- [ ] `[P1]` Verify every `\ref`/`\cref` resolves to the correct Fig./Tab./Eq./section.
  (FR-16)

### M5.4 — Diagnostics
- [ ] `[P0]` On failure, surface a concise log excerpt and the failing pass to the user
  and the QA Agent. (FR-19, NFR-5)
- [ ] `[P1]` Classify common errors (missing package, missing asset, undefined control
  sequence, undefined citation). (FR-19, R-4, R-6)
- [ ] `[P2]` Persist full logs under `build/` for post-mortem. (NFR-8)

### M5 — Exit gate
- [ ] `[P0]` ✅ Milestone M5 sign-off: clean build; all citations/refs clickable and
  resolving. (plan.md M5 exit criteria)

---

## Phase M6 — QA, Hardening & Handoff

> Goal: Run the QA checklist (FR-20), surface diagnostics, and provide a single-command
> entry point. Exit: the Definition of Done in `prd.md` §9 is fully satisfied.

### M6.1 — Link & cross-reference validation
- [ ] `[P0]` Verify all internal hyperlinks resolve (no dead links). (FR-20, US-8)
- [ ] `[P0]` Click-test that a sample citation jumps to its bibliography entry. (FR-16)
  > Note: If clicking a reference does not jump, treat it as a compilation issue. (R-3)
- [ ] `[P1]` Parse the log/PDF for any remaining `??` or "undefined reference". (FR-20)

### M6.2 — Bibliography verification
- [ ] `[P0]` Confirm every in-text citation has a matching `.bib` entry. (FR-16, R-3)
- [ ] `[P0]` Confirm no orphan `.bib` entries and no missing citations. (FR-16)
- [ ] `[P1]` Confirm bibliography formatting/style is consistent. (NFR-10)

### M6.3 — Required-elements audit (FR-9)
- [ ] `[P0]` Confirm the **diagram** is present and referenced. (FR-9)
- [ ] `[P0]` Confirm the **image** is present and referenced. (FR-9)
- [ ] `[P0]` Confirm the **Python-generated graph** is present and referenced. (FR-9)
- [ ] `[P0]` Confirm at least one **table** is present and in the index. (FR-9)
- [ ] `[P0]` Confirm at least one **decorated formula** is typeset (not plain text). (FR-10)
- [ ] `[P1]` Confirm Table/Figure index entries do not break visual marking. (FR-20)

### M6.4 — Page count & structure checks
- [ ] `[P0]` Verify the final PDF is **15–20 pages**. (FR-7, R-5)
  > Note: If under/over, adjust per-chapter budgets in M2.2 and rebuild.
- [ ] `[P1]` Verify cover (title/author/date/language), TOC, and headers/footers present.
  (FR-8, FR-12)
- [ ] `[P1]` Verify chapter/section hierarchy matches the outline. (FR-8)

### M6.5 — BiDi correctness review
- [ ] `[P0]` Visually verify the BiDi chapter's RTL↔LTR transitions are correct. (FR-13)
- [ ] `[P1]` Verify LTR islands (terms, numbers, code) read correctly within RTL. (FR-13, R-1)
- [ ] `[P1]` For Hebrew runs, verify full RTL layout across the whole document. (FR-14)

### M6.6 — Hardening & handoff
- [ ] `[P0]` Provide a single-command entry point that runs the full pipeline. (US-1)
- [ ] `[P1]` Confirm zero manual edits are required between run start and final PDF.
  (success metric: manual intervention = 0)
- [ ] `[P1]` Re-run with the same config to confirm reproducibility. (NFR-3)
- [ ] `[P2]` Ensure no secrets appear in logs or artifacts. (NFR-9, R-10)

### M6 — Exit gate
- [ ] `[P0]` ✅ Milestone M6 sign-off: Definition of Done (`prd.md` §9) fully satisfied.
  (plan.md M6 exit criteria)

---

## Cross-Cutting: Validation & QA Checklist

> Consolidated success-metric verification (mirrors `prd.md` §6). Run before final handoff.

- [ ] `[P0]` **Requirement compliance:** 100% of FR-9 elements present. (FR-9)
- [ ] `[P0]` **Page count:** final PDF is 15–20 pages. (FR-7)
- [ ] `[P0]` **Link integrity:** 100% of citations/cross-references resolve. (FR-16)
- [ ] `[P0]` **Bibliography correctness:** all cited entries present; no orphans. (FR-16)
- [ ] `[P0]` **BiDi correctness:** ≥1 chapter with verified RTL↔LTR transitions. (FR-13)
- [ ] `[P0]` **Compilation success:** clean build after the prescribed sequence. (FR-18)
- [ ] `[P0]` **Formula typesetting:** 0 plain-text formulas. (FR-10)
- [ ] `[P1]` **Reproducibility:** same config yields a compiling project. (NFR-3)
- [ ] `[P1]` **Manual intervention:** zero manual edits start-to-PDF. (US-1)

---

## Cross-Cutting: Risk-Mitigation Tasks (plan.md §6)

- [ ] `[P0]` **R-1 BiDi:** LuaLaTeX + polyglossia/bidi + Hebrew font; `\LR{}` islands;
  dedicated visual QA. (R-1)
- [ ] `[P0]` **R-2 Formulas:** enforce `amsmath` environments in the skill; QA rejects
  plain-text formulas. (R-2)
- [ ] `[P0]` **R-3 Refs/citations:** automate canonical passes; loop on "rerun" warnings.
  (R-3)
- [ ] `[P1]` **R-4 Figure paths:** standardized `figures/` layout; pre-build asset check.
  (R-4)
- [ ] `[P1]` **R-5 Page count:** per-chapter page budget; iterate before assembly. (R-5)
- [ ] `[P1]` **R-6 MiKTeX/engine:** verify toolchain in M0; pre-install packages. (R-6)
- [ ] `[P1]` **R-7 LLM inconsistency:** skill-driven constraints + Markdown review gate.
  (R-7)
- [ ] `[P1]` **R-8 Conversion loss:** controlled Markdown→LaTeX; validate elements. (R-8)
- [ ] `[P2]` **R-9 Reproducibility:** pin model/config; persist intermediate artifacts.
  (R-9)
- [ ] `[P0]` **R-10 Secrets:** load from env/secret storage; never log or hard-code. (R-10)

---

## Appendix A — Definition of Done (prd.md §9)

A single run produces a 15–20 page PDF that contains:
- [ ] Thematic cover with title, author, date, and language. (FR-12)
- [ ] Table of contents. (FR-8)
- [ ] Chapters with headers/footers. (FR-8)
- [ ] At least one diagram. (FR-9)
- [ ] At least one image. (FR-9)
- [ ] At least one Python-generated graph. (FR-9)
- [ ] At least one table. (FR-9)
- [ ] At least one decorated mathematical formula. (FR-10)
- [ ] A chapter with correct BiDi (RTL↔LTR) handling. (FR-13)
- [ ] A linked bibliography from a `.bib` source. (FR-15, FR-16)
- [ ] All internal links and citations resolving after the canonical compile sequence.
  (FR-16, FR-18)

---

## Appendix B — Backlog Maintenance Notes

- Keep task IDs/section anchors (`§Mx.y`) stable so the traceability table stays valid.
- When a requirement changes in `prd.md`, update the matching `(FR-n)`-tagged tasks here.
- Promote recurring manual checks into automated validation tasks where practical. (NFR-5)
- Do not delete completed tasks; check them off to preserve an audit trail. (NFR-8)

---

## Appendix C — Per-Skill Authoring Checklist

> Every `SKILL.md` must have YAML front matter (`name`, `description`, `metadata`) and a
> focused Markdown body. The `description` is the agent's selection signal.

### C.1 — `technical-writing`
- [ ] `[P0]` Define document tone, voice, and house style. (FR-2)
- [ ] `[P1]` Define chapter/section heading conventions. (FR-8)
- [ ] `[P1]` Define how to place figure/table/equation anchors in Markdown. (FR-9)
- [ ] `[P2]` Provide a short "good vs. bad paragraph" example in `references/`. (NFR-10)

### C.2 — `bidi-hebrew`
- [ ] `[P0]` Specify base direction rules (RTL default for Hebrew). (FR-14)
- [ ] `[P0]` Specify how to wrap LTR islands (English, numerals, code). (FR-13, R-1)
- [ ] `[P1]` Provide examples of correct vs. broken mixed-direction sentences. (R-1)
- [ ] `[P2]` Note common BiDi pitfalls (punctuation, parentheses ordering). (R-1)

### C.3 — `latex-authoring`
- [ ] `[P0]` Specify preamble template and required packages. (FR-4)
- [ ] `[P0]` Mandate `amsmath` math environments; forbid plain-text formulas. (FR-10, R-2)
- [ ] `[P1]` Specify `\label`/`\cref` conventions for refs. (FR-16)
- [ ] `[P1]` Specify Markdown→LaTeX conversion rules for tables and math. (R-8)
- [ ] `[P2]` Provide a minimal compilable `.tex` example in `references/`. (NFR-10)

### C.4 — `figure-generation`
- [ ] `[P0]` Specify `figures/` naming and relative-path conventions. (FR-11, R-4)
- [ ] `[P0]` Specify vector-preferred export (PDF) for diagram/graph. (FR-9)
- [ ] `[P1]` Provide a Matplotlib script template in `scripts/`. (FR-9, NFR-3)
- [ ] `[P2]` Specify caption + label requirements per asset. (FR-16)

### C.5 — `qa-checklist`
- [ ] `[P0]` Encode the FR-20 technical contract as an ordered checklist. (FR-20)
- [ ] `[P1]` Encode page-count and required-elements audit steps. (FR-7, FR-9)
- [ ] `[P1]` Encode link/citation resolution checks. (FR-16)

### C.6 — `research-methodology`
- [ ] `[P0]` Specify source-vetting criteria and how to reject weak sources. (R-7)
- [ ] `[P0]` Specify the exact `.bib` entry format and key naming. (FR-15)
- [ ] `[P2]` Provide a sample `.bib` entry in `references/`. (NFR-10)

### C.7 — `document-structure`
- [ ] `[P0]` Specify how to size an outline to a 15–20 page target. (FR-7)
- [ ] `[P1]` Specify per-chapter page budgeting heuristics. (R-5)
- [ ] `[P2]` Specify where the BiDi chapter fits in the structure. (FR-13)

---

## Appendix D — Agent & Tool Inventory

> Confirm each agent has the right Skills (the "how") and Tools (the "what").

- [ ] `[P0]` **Research Agent** — skill: `research-methodology`; tools: web/search,
  file-read. (FR-1, FR-2)
- [ ] `[P0]` **Outline/Architect Agent** — skill: `document-structure`; tools:
  file read/write. (FR-1)
- [ ] `[P0]` **Writer Agent** — skills: `technical-writing`, `bidi-hebrew`; tools:
  file-write. (FR-1, FR-13)
- [ ] `[P0]` **Figure/Graph Agent** — skill: `figure-generation`; tools: Python exec,
  file-write. (FR-1, FR-9)
- [ ] `[P0]` **LaTeX Builder Agent** — skill: `latex-authoring`; tools: file read/write.
  (FR-4)
- [ ] `[P0]` **Compilation Agent** — tools: shell/process exec. (FR-17)
- [ ] `[P0]` **QA/Review Agent** — skill: `qa-checklist`; tools: file-read, log parse.
  (FR-20)
- [ ] `[P2]` Confirm no agent is missing a required tool for its task. (NFR-5)

---

## Appendix E — LaTeX Preamble Package Checklist

> Confirm the preamble declares every package needed for the requirements.

- [ ] `[P0]` `fontspec` — Unicode/OpenType font loading (LuaLaTeX/XeLaTeX). (FR-14)
- [ ] `[P0]` `polyglossia` (or `babel`) — Hebrew + English languages. (FR-13, FR-14)
- [ ] `[P0]` `amsmath`, `amssymb` — math typesetting. (FR-10)
- [ ] `[P1]` `mathtools` — extended/decorated math constructs. (FR-10)
- [ ] `[P0]` `graphicx` — `\includegraphics` for image/graph/diagram. (FR-9, FR-11)
- [ ] `[P1]` `tikz` — native diagram option. (FR-9)
- [ ] `[P1]` `booktabs` — professional tables. (FR-9)
- [ ] `[P0]` `hyperref` — clickable links, TOC, citations. (FR-16)
- [ ] `[P1]` `cleveref` — typed cross-references. (FR-16)
- [ ] `[P0]` `fancyhdr` — headers/footers. (FR-8)
- [ ] `[P0]` `biblatex` (+ biber) or `natbib` (+ bibtex) — bibliography. (FR-15, FR-16)
- [ ] `[P2]` Confirm package load order avoids `hyperref` conflicts. (R-6)

---

## Appendix F — Dependency-Ordered Execution Board

> Suggested critical path. Items on the same line can proceed in parallel.

- [ ] `[P0]` 1. M0 toolchain + skeleton (blocks everything). (M0)
- [ ] `[P0]` 2. M1 skills + agents + crew wiring. (M1)
- [ ] `[P0]` 3. M2 outline → Markdown draft + `.bib` (gated by human review). (M2)
- [ ] `[P0]` 4. M3 figures/tables/formulas (parallelizable per asset). (M3)
- [ ] `[P0]` 5. M4 LaTeX assembly (needs M2 content + M3 assets). (M4)
- [ ] `[P0]` 6. M5 multi-pass compilation + link resolution (needs M4). (M5)
- [ ] `[P0]` 7. M6 QA + hardening + handoff (needs M5). (M6)
- [ ] `[P1]` 8. Final validation checklist + Definition of Done sign-off. (prd.md §9)

> Note: Figure generation (M3) can start as soon as the outline (M2.2) defines where each
> asset belongs, overlapping with drafting (M2.3) to shorten the critical path. (NFR-2)

---

## Appendix G — Environment & Reproducibility Matrix

> Confirm the run environment is captured so results are reproducible. (NFR-3, NFR-4)

- [ ] `[P1]` Record OS and shell used for the run. (NFR-4)
- [ ] `[P1]` Record MiKTeX version and selected engine (LuaLaTeX/XeLaTeX). (FR-17, NFR-3)
- [ ] `[P1]` Record Python version and Matplotlib version. (FR-9, NFR-3)
- [ ] `[P1]` Record CrewAI version and the LLM model/provider used. (FR-1, NFR-3)
- [ ] `[P1]` Record the Hebrew font name and version. (FR-14, NFR-3)
- [ ] `[P2]` Pin model temperature/seed in config for deterministic drafting. (NFR-3)
- [ ] `[P2]` Store all intermediate artifacts (Markdown, `.tex`, figures, logs). (NFR-8)

---

## Appendix H — Final Acceptance Sign-Off

> Single consolidated gate before delivery. All boxes must be checked.

- [ ] `[P0]` All milestone exit gates (M0–M6) are signed off.
- [ ] `[P0]` All Definition of Done items (Appendix A) are checked.
- [ ] `[P0]` All cross-cutting validation/QA items pass.
- [ ] `[P0]` All P0 risk-mitigation tasks are complete.
- [ ] `[P1]` Reproducibility matrix (Appendix G) is filled in.
- [ ] `[P1]` Final PDF reviewed and approved for submission.
- [ ] `[P0]` Sign-off: ____________________  Date: ____________
