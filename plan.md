# Implementation Plan

## Multi-Agent Article/Book Generation System with CrewAI and LaTeX

| Field | Value |
|-------|-------|
| Document version | 1.0 |
| Status | Draft for review |
| Author | Senior Software Engineer |
| Last updated | 2026-05-30 |
| Related document | `prd.md` (Product Requirements Document) |

---

## 1. Technical Architecture

### 1.1 High-Level Design
The system is a **linear-with-feedback CrewAI pipeline**. Each agent is single-responsibility
and communicates through shared task outputs and a structured working directory. Domain
expertise is injected through **Skills** (`.md` packages); operational ability is provided
through **Tools**. The flow is **Markdown-first**: content is drafted and reviewed in
Markdown, then converted to `.tex` and compiled through a multi-pass LaTeX toolchain.

```
Topic + Language
      │
      ▼
[Research Agent] ──► [Outline/Architect Agent] ──► [Writer Agent]
                                                        │
                          ┌─────────────────────────────┤
                          ▼                             ▼
              [Figure/Graph Agent]            (Markdown chapters)
                          │                             │
                          └──────────────┬──────────────┘
                                         ▼
                              [LaTeX Builder Agent]
                                         ▼
                              [Compilation Agent] ◄─┐
                                         ▼          │ (retry on
                                  [QA/Review Agent] ─┘  unresolved refs)
                                         ▼
                                   Final PDF
```

### 1.2 Agent Responsibilities
| Agent | Responsibility | Key Skill | Key Tools |
|-------|----------------|-----------|-----------|
| Research | Gather sources, build `.bib` entries | research-methodology | Web/search, file read |
| Outline/Architect | Define chapter/section structure, page budget | document-structure | File read/write |
| Writer | Draft chapter content in Markdown (incl. BiDi chapter) | technical-writing, bidi-hebrew | File write |
| Figure/Graph | Generate diagram, image, Python graph, table | figure-generation | Python exec, file write |
| LaTeX Builder | Convert Markdown → `.tex`, wire preamble/cover/TOC | latex-authoring | File read/write |
| Compilation | Run engine + bib + repeated passes | latex-compilation | Shell/process exec |
| QA/Review | Verify links, citations, indexes, formulas, page count | qa-checklist | File read, log parse |

### 1.3 Skills Layout
Skills follow the CrewAI convention: an independent folder per skill with a required
`SKILL.md` (YAML front matter + Markdown instructions), plus optional `references/` and
`scripts/` folders. Skills are injected per-agent via `skills=[...]`, with crew-level
defaults overridable at agent level, or loaded programmatically with
`discover_skills` / `activate_skill`.

```
skills/
  technical-writing/    SKILL.md  references/  scripts/
  bidi-hebrew/          SKILL.md
  latex-authoring/      SKILL.md  references/
  figure-generation/    SKILL.md  scripts/
  qa-checklist/         SKILL.md
```

### 1.4 Project Working Directory
```
project/
  content/      *.md            # reviewable Markdown drafts
  figures/      *.png *.pdf     # Python-generated graphs, image, diagram
  scripts/      *.py            # plotting/diagram scripts
  latex/
    main.tex                    # preamble, cover, TOC, includes
    chapters/   *.tex
    references.bib              # bibliography source
  build/        main.pdf, *.log # compiled output + diagnostics
```

---

## 2. Recommended Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Orchestration | **CrewAI** | Required; agent-team model with Skills + Tools |
| LLM | Configurable provider (env-based credentials) | Decoupled from orchestration; swappable |
| Authoring format | **Markdown → LaTeX** | Fast review, then high-quality typesetting |
| LaTeX distribution | **MiKTeX** | Required; bundles engines and bib tools |
| LaTeX engine | **LuaLaTeX** (primary), XeLaTeX (fallback) | Strong Unicode + Hebrew BiDi support |
| Bibliography | **`.bib` + biber/BibTeX** | Linked citations, standard tooling |
| BiDi/RTL | `babel`/`polyglossia` + `bidi`, Hebrew Unicode font | Correct RTL↔LTR transitions |
| Math | `amsmath`, `amssymb` (+ `mathtools`) | Decorated, properly typeset formulas |
| Cross-refs/links | `hyperref`, `cleveref` | Clickable citations and references |
| Headers/footers | `fancyhdr` | Required header/footer support |
| Graphs | **Python + Matplotlib** | Python-generated graph requirement |
| Diagrams | TikZ or Python-exported vector image | Diagram requirement, scalable output |
| Process control | Python subprocess / shell tool | Drives multi-pass compilation |

---

## 3. Phased Implementation Schedule

### Phase 0 — Environment & Scaffolding (Milestone M0)
- Install/verify MiKTeX (LuaLaTeX, biber), Python + Matplotlib, CrewAI.
- Verify a Hebrew-capable Unicode font is available.
- Create the project working-directory skeleton and a minimal compiling `main.tex`.
- **Exit criteria:** "hello world" `.tex` with cover + TOC compiles to PDF via the full pass sequence.

### Phase 1 — Skills & Agent Definitions (Milestone M1)
- Author `SKILL.md` files for each skill (writing, BiDi, LaTeX, figures, QA).
- Define all agents with roles, goals, backstories, attached skills and tools.
- Wire the crew with task ordering and shared working directory.
- **Exit criteria:** crew runs end-to-end on a stub topic producing placeholder artifacts.

### Phase 2 — Content Pipeline (Milestone M2)
- Implement Research → `.bib` generation and Outline → page-budgeted structure.
- Implement Writer producing Markdown chapters, including the BiDi chapter.
- **Exit criteria:** complete, reviewable Markdown draft (15–20 page estimate) with sources.

### Phase 3 — Figures, Tables & Formulas (Milestone M3)
- Generate the Python graph (Matplotlib), the diagram (TikZ/vector), and the image asset.
- Author at least one table and at least one decorated mathematical formula.
- Save all assets to `figures/` with correct relative paths referenced in `.tex`.
- **Exit criteria:** all FR-9 required elements exist on disk and resolve in the source.

### Phase 4 — LaTeX Assembly (Milestone M4)
- LaTeX Builder converts finalized Markdown to `.tex`; wires preamble, cover (title,
  author, date, language), TOC, `fancyhdr` headers/footers, `hyperref`/`cleveref`.
- Configure BiDi packages and Hebrew font; integrate `references.bib`.
- **Exit criteria:** assembled project compiles once with placeholders for unresolved refs.

### Phase 5 — Compilation & Link Resolution (Milestone M5)
- Implement the prescribed pass sequence (see §4) in the Compilation agent.
- Resolve all cross-references and citation links across repeated passes.
- **Exit criteria:** clean build; all citations/refs clickable and resolving.

### Phase 6 — QA, Hardening & Handoff (Milestone M6)
- Run the QA checklist: links resolve, citations exist, Table/Figure indexes intact,
  formulas typeset (no plain text), BiDi correct, page count 15–20.
- Add diagnostics surfacing and a single-command entry point.
- **Exit criteria:** Definition of Done in `prd.md` §9 fully satisfied.

| Milestone | Deliverable |
|-----------|-------------|
| M0 | Toolchain verified + minimal compiling skeleton |
| M1 | Skills authored + crew wired end-to-end |
| M2 | Complete reviewable Markdown draft + `.bib` |
| M3 | All required figures/tables/formulas generated |
| M4 | Assembled compilable `.tex` project |
| M5 | Clean multi-pass build with resolved links |
| M6 | QA-passed, requirement-compliant final PDF |

---

## 4. Compilation Sequence (Canonical)

The Compilation agent executes the following deterministic sequence and treats unresolved
references as expected until the final passes:

1. `lualatex main.tex`  (initial pass; builds `.aux`)
2. `biber main`  (or `bibtex main`) — resolves bibliography
3. `lualatex main.tex`  (pass 2 — pulls in citations)
4. `lualatex main.tex`  (pass 3 — resolves cross-references/TOC)
5. `lualatex main.tex`  (optional pass 4 — stabilizes page numbers/links)

A successful build is one where consecutive passes produce no "rerun" warnings and no
unresolved `??` references. XeLaTeX may substitute for LuaLaTeX if required.

---

## 5. Testing & Validation Strategy

| Level | Check | Method |
|-------|-------|--------|
| Unit | Python figure scripts produce expected output files | Run scripts; assert files exist and are non-empty |
| Unit | Skill files parse (valid YAML front matter) | Lint `SKILL.md` files |
| Integration | Crew runs stages in order, passing artifacts | Stub-topic dry run |
| Build | Project compiles through full pass sequence | Automated compile + log scan for errors/warnings |
| Contract | Links/citations resolve; no `??` markers | Parse `.log`/PDF for unresolved refs |
| Contract | All FR-9 elements present | QA checklist asserts diagram/image/graph/table/formula |
| Contract | Page count within 15–20 | PDF page-count check |
| Manual | BiDi chapter renders correctly | Visual review of RTL↔LTR transitions |

Tests should be added as the corresponding phase completes; a final regression run
validates the entire Definition of Done.

---

## 6. Risk Assessment & Mitigation

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R-1 | Hebrew BiDi renders incorrectly (reversed terms, broken LTR islands) | High | High | Use LuaLaTeX + `polyglossia`/`bidi` with a Hebrew Unicode font; isolate English with `\LR{}`; dedicate a QA visual check |
| R-2 | Formula emitted as plain text due to Hebrew–English mixing | Medium | High | Enforce `amsmath` environments in the latex-authoring skill; QA scans for math environments, rejects plain-text formulas |
| R-3 | Citations/cross-refs don't resolve (insufficient passes) | Medium | High | Automate the canonical pass sequence (§4); detect "rerun" warnings and loop up to a safe max |
| R-4 | Figure paths broken; LaTeX can't find graphics | Medium | Medium | Standardize `figures/` layout and relative paths; QA verifies every `\includegraphics` target exists |
| R-5 | Page count outside 15–20 | Medium | Medium | Outline agent enforces a page budget per chapter; iterate content length before assembly |
| R-6 | MiKTeX on-the-fly package install fails / missing engine | Low | High | Verify toolchain in Phase 0; pre-install required packages; document prerequisites |
| R-7 | LLM produces inconsistent structure or hallucinated sources | Medium | Medium | Skill-driven constraints + human Markdown review gate before LaTeX conversion |
| R-8 | Markdown→LaTeX conversion drops structure (tables, math) | Medium | Medium | Use a controlled conversion in the LaTeX Builder skill; validate against required elements |
| R-9 | Non-deterministic runs hinder reproducibility | Low | Medium | Pin model/config; persist all intermediate artifacts to the working directory |
| R-10 | API credential leakage | Low | High | Load keys from environment/secret storage; never log or hard-code secrets |

---

## 7. Maintainability & Scalability Notes

- **Modularity:** Adding a chapter, figure type, or quality rule means adding/editing a
  skill `.md` or a task — not rewriting orchestration.
- **Separation of concerns:** Knowledge lives in Skills; capability lives in Tools;
  structure lives in the working directory; control lives in the crew definition.
- **Extensibility:** New agents (e.g., translator, index generator) slot into the pipeline
  without disturbing existing stages.
- **Observability:** Every stage persists artifacts and logs, enabling targeted debugging
  and reproducible re-runs.

## 8. Definition of Done

Aligned with `prd.md` §9: a single run yields a 15–20 page PDF with a thematic cover, TOC,
chaptered structure with headers/footers, all required graphical/tabular/mathematical
elements, a verified BiDi chapter, and a linked bibliography — with all internal links and
citations resolving after the canonical compilation sequence.

---

## 9. Architecture Decision Records (ADRs)

These records justify the framework boundaries so an evaluator can see what was
considered and deliberately excluded.

### ADR-001 — CrewAI as the sole orchestration framework
- **Decision:** Use **CrewAI** (Agent / Task / Crew, `Process.sequential`) for all
  orchestration; do **not** add LangChain, LangGraph, or A2A.
- **Rationale:** LangChain, LangGraph, A2A, and CrewAI all occupy the *orchestration /
  control-flow* layer and therefore compete — one is enough. The pipeline is a fixed
  linear flow (research → outline → write → figures → LaTeX → compile → QA) with
  role-based agents, which is exactly CrewAI's model. LangChain's linear chains are a
  subset of what CrewAI provides; A2A solves cross-system/cross-vendor agent interop that
  does not exist here (single local process; handoffs use `context=[...]` + the shared
  working directory).
- **Revisit if:** the flow needs dynamic branching, conditional re-planning, or stateful
  loops with checkpoints → **LangGraph** would then become the stronger orchestrator.

### ADR-002 — Compilation loop is plain Python, not an agent state machine
- **Decision:** Implement the M5 "recompile until references resolve" loop as a
  **deterministic Python `subprocess` driver**, not a LangGraph graph or an LLM agent loop.
- **Rationale:** The canonical sequence (`lualatex → biber → lualatex ×2–3`, looping on
  "rerun" warnings up to a safe cap) is deterministic and cheaper, more reliable, and more
  testable as code than as agent reasoning. The Compilation agent simply *invokes* the
  driver tool.

### ADR-003 — RAG / vector DB is OPTIONAL, not core
- **Decision:** Ship **without** RAG by default; provide an **optional, lightweight,
  local** retrieval track (see §10.6 / M9) gated behind a config flag.
- **Rationale:** The corpus is small and curated, and the grading requirement is
  *bibliography correctness* (every in-text citation resolves to a `.bib` entry), not broad
  knowledge retrieval. The real risk is *hallucinated citations* (R-7), mitigated more
  cheaply by the `research-methodology` skill plus the M6 `.bib`↔in-text consistency check
  than by a vector store. CrewAI does **not** replace RAG (RAG is a knowledge layer, not an
  orchestration layer); we omit RAG on its own merits, not because CrewAI covers it.
- **Revisit if:** sources must be live, verifiable, or numerous → enable the M9 retriever
  tool (Chroma/FAISS + local embeddings) wrapped as a CrewAI tool for the Research agent.

### ADR-004 — Provider now, config seam for local later
- **Decision:** Use the **OpenAI provider** for LLM runs now; route all model construction
  through the Gatekeeper with a `provider`/`model` config seam so **Ollama / Hugging Face**
  can be added later without touching agents.
- **Rationale:** Provider quality is needed for coursework output; a config seam keeps a
  local/offline/cost-reduced path open without lock-in. Cloud deployment stays out of scope
  (local CLI per PRD §1.4). The deterministic `--stub` path remains the zero-cost lane.

---

## 10. Production-Hardening Architecture (Audit Follow-up)

This section captures the components needed to move from "strong PoC" to production-grade
(repeatable, observable, modular, secure, testable, maintainable). All changes are
**additive and backward-compatible**; the existing `--stub` path and CLI are preserved.

### 10.1 Explicit Harness
Make the implicit harness explicit and centralized so all 7 agents share one instrumented
path: **input validation (`inputs.py`) → prompt/skill construction → sandboxed context
assembly → model call (via Gatekeeper) → output parse/validate → logging + cost/latency →
error handling + retries → guarded artifact write → final run report.** The missing middle
is *call wrapping, output validation, and observability* (added in M7–M9).

### 10.2 Gatekeeper hardening
Promote `shared/gatekeeper.py` from an "LLM factory" to a **call wrapper**: config-driven
**retries with backoff, timeout, optional rate limit/backpressure**, and **token/latency/
cost capture**. `create_llm` signature is preserved for backward compatibility.

### 10.3 Security & human-in-the-loop
Add a thin guard layer (`shared/security.py`): input sanitization beyond length (control
chars + simple instruction-injection heuristics on `topic`), a trust note for content fed
into context (mitigate prompt injection / memory poisoning via files), an **overwrite
dry-run guard** for `write_workspace_file`, and an explicit **human-approval gate before the
paid LLM path** (`--yes` to bypass in automation). Existing boundaries (path allowlist, no
arbitrary code exec, secret hygiene) are retained. Ship red-team test cases.

### 10.4 Observability & run report
Add `shared/observability.py`: a **run context** (`run_id`, timestamps) and a structured
logger recording per-task inputs/outputs (redacted), token usage, latency, retries, and
errors, then writing a single `build/run_report_<run_id>.{json,md}`. Hook into the existing
`task_callback` in `pipeline.run_llm` and the Gatekeeper so a reviewer can reconstruct *why*
an agent decided something.

### 10.5 Configuration & versioning
Externalize hardcoded settings into a versioned `config/` tree (Python defaults remain
fallback): `config/models.yaml` (provider/model/temperature/seed/retries/limits),
`config/agents.yaml` (role/goal/backstory/skills/tools), `config/tasks.yaml` (task
descriptions + `expected_output` — a prompt registry). Each carries a `version` field
(skills already do). This versions prompts, agents, tasks, and RAG/output schema.

### 10.6 RAG & Vector DB (OPTIONAL — see ADR-003)
Default: **off**. When enabled via `config/models.yaml` (`rag.enabled: true`), provide a
**lightweight local** retrieval pipeline wrapped as a single CrewAI tool for the Research
agent:

| Component | Choice (minimal) |
|-----------|------------------|
| Document loader | Local files under a `knowledge/` folder (txt/md/pdf) |
| Text splitter | Simple recursive character splitter (fixed size/overlap) |
| Embeddings | Local model (e.g. `sentence-transformers`) to avoid extra API cost |
| Vector store | **Chroma** or **FAISS** (local, file-backed; no server) |
| Retriever | top-k similarity, returned as cited snippets |
| Prompt template | Inject retrieved snippets + source IDs into the research task |
| Citation handling | Map retrieved source IDs → `.bib` keys (feeds M6 consistency check) |
| Output parser | Structured `{claim, source_id}` list for the Writer/`.bib` step |

**Decision gate:** keep RAG **disabled** while the curated/stub corpus satisfies the
bibliography contract; enable only if live or numerous sources are required. This honors
"add it, unless it's simple" — it is wired into the plan but not on the default path.

### 10.7 Provider / local / cloud strategy
- **Now:** OpenAI provider (quality) + `--stub` (offline/CI, zero cost).
- **Later:** add Ollama/HF behind the Gatekeeper `provider` seam for cost/privacy.
- **Cloud:** out of scope (local CLI); no change recommended.

---

## 11. Production-Hardening Schedule (Milestones M7–M9)

> These milestones run **alongside / after** the still-pending product milestones
> **M5** (multi-pass compile + biber) and **M6** (QA contract + page count), which remain
> the highest priority for a gradeable PDF. M7–M9 raise the system to production grade.

### Phase 7 — Production Harness, Gatekeeper & Config (Milestone M7)
- Wrap the Gatekeeper (retries/backoff/timeout/cost+latency capture); add output validation.
- Externalize settings into `config/{models,agents,tasks}.yaml` with Python fallback.
- Add `skills/compilation/SKILL.md` (canonical pass sequence) for the Compilation agent.
- **Exit criteria:** LLM calls are retried/timed/costed; agents/tasks load from config;
  `--stub` and CLI unchanged; new unit tests green.

### Phase 8 — Security & Human-in-the-Loop (Milestone M8)
- Add `shared/security.py` (input/output guards, injection heuristics, overwrite dry-run).
- Add a human-approval gate before the paid LLM path (`--dry-run`, `--yes` CLI flags).
- Add `skills/security-review/SKILL.md` for the QA/security gate.
- **Exit criteria:** red-team tests pass (injection-via-topic rejected, traversal blocked,
  poisoned-file handled, dry-run blocks overwrite); approval gate enforced by default.

### Phase 9 — Observability & Run Reporting (Milestone M9)
- Add `shared/observability.py` (run_id, structured logs, token/latency/error capture).
- Emit `build/run_report_<run_id>.{json,md}` aggregating every stage.
- **Exit criteria:** a single run produces a complete, redacted, replayable report.

### Phase 9-OPT — RAG + Vector DB (Optional, gated by ADR-003)
- Implement the §10.6 local retriever (Chroma/FAISS + local embeddings), wrapped as a
  CrewAI tool, **disabled by default** (`rag.enabled: false`).
- **Exit criteria (only if enabled):** retriever returns cited snippets mapped to `.bib`
  keys; M6 consistency check passes against retrieved sources.

| Milestone | Deliverable |
|-----------|-------------|
| M7 | Hardened Gatekeeper + config-driven agents/tasks + compilation skill |
| M8 | Security guards + human-approval gate + security-review skill |
| M9 | Structured observability + per-run report |
| M9-OPT | Optional local RAG/vector-DB retriever (off by default) |
