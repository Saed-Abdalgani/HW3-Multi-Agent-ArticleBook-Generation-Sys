# AI-Assisted Development Log (PROMPTS.md)

> **Note:** The tracked filename is `PROMPTS.md` (all caps). Some tools or assignments refer to it as `prompts.md`; they are the same document.

## HW3 — Multi-Agent Article/Book Generation (CrewAI + LaTeX)

| Field | Value |
|-------|-------|
| Version | 3.08 |
| Updated | 2026-06-01 |
| Related docs | [README.md](README.md), [prd.md](prd.md), [plan.md](plan.md), [todo.md](todo.md) |

---

## Purpose

This document records significant AI-assisted development interactions: context, purpose, output summaries, and lessons learned. It provides transparency about AI contributions and supports reproducibility of the development process.

---

## HW3 project snapshot

- **Goal:** A **CrewAI** crew of specialized agents researches, outlines, writes, and typesets a **15–20 page** LaTeX document on a user-chosen topic, producing a **print-ready PDF** (see [prd.md](prd.md)).
- **Flow (target):** **Markdown-first** authoring in a structured working tree, then Markdown → `.tex`, multi-pass **LuaLaTeX** + **biber/BibTeX**, with diagram / image / Python graph / table / math and **Hebrew–English BiDi** where required ([plan.md](plan.md) §1).
- **Skills:** Per-agent **CrewAI Skills** live under `skills/*/SKILL.md` (see [plan.md](plan.md) §1.3); **M1** delivered the tree plus a crew-level `house-culture` skill.
- **Tools:** Sandboxed workspace tools in `articlebook.crew.workspace_tools` (writes under `content/`, `latex/`, `figures/`, `build/`, `scripts/`; reads selected root docs). Optional web search tools remain future work behind Gatekeeper.
- **Toolchain:** **MiKTeX** on Windows; `compile_latex_canonical` prepends default user MiKTeX `bin` when engines are missing from `PATH`. **`ARTICLEBOOK_LATEX_ENGINE`** selects `lualatex` vs `xelatex`. Bibliography: **biber** between passes ([docs/PRD_m5_compile.md](docs/PRD_m5_compile.md)); QA contract expands in M6 ([prd.md](prd.md) FR-17–FR-20).
- **Configuration:** `articlebook.shared.config` merges **`config/models.yaml`** with `.env` (`python-dotenv`): `OPENAI_API_KEY` (+ optional `_2` / `_3`), or **`ARTICLEBOOK_OPENROUTER_KEY_SUFFIX`** / **`ARTICLEBOOK_GROQ_KEY_SUFFIX`** / **`ARTICLEBOOK_NVIDIA_KEY_SUFFIX`** (see **`.env_example`**), or **`ARTICLEBOOK_LLM_ROUTES`** for explicit `api_key|model` slots; `MODEL_NAME` (ignored when routes/suffix triple are active), `TEMPERATURE`, `SEED`, `ARTICLEBOOK_LLM_PROVIDER`, `ARTICLEBOOK_LLM_TIMEOUT_S`, `ARTICLEBOOK_CONFIG_DIR`, gatekeeper knobs (`ARTICLEBOOK_GK_*`). **`config/agents.yaml`** / **`config/tasks.yaml`** overlay agent copy and M2 task prompts. Env vars are listed in **README** (local `.env` only; never commit secrets).
- **Dependencies:** Declared in [pyproject.toml](pyproject.toml); lock with [uv.lock](uv.lock) via `uv lock`. [requirements.txt](requirements.txt) is a pointer only.
- **Reproducibility notes:** [versions.txt](versions.txt) is referenced in [todo.md](todo.md) for recording installed tool versions.
- **Repo layout (present):** `src/articlebook/` package, `skills/`, `content/`, `figures/`, `scripts/`, `latex/` (with `chapters/`), `build/` (compile output); placeholders via `.gitkeep` where empty.
- **Current implementation status:** **M1–M7** — M7 adds `InstrumentedLLM` (retries/backoff, timeout, optional min interval, per-call latency + token delta + rough cost), `config/*.yaml`, `build/resolved_run_config.json`, `skills/compilation`, M2 task YAML overrides; see [docs/PRD_m7_production_harness.md](docs/PRD_m7_production_harness.md). **M6** DoD (manual BiDi PDF, full PDF without `--m6-allow-missing-pdf`) and **M8–M9** remain per [todo.md](todo.md).

---

## General requirements

Two things live under this heading: (1) **what the assignment PDF must contain**, and (2) **how large Python modules should be** so the codebase stays reviewable as the crew grows.

### Assignment / PRD (deliverable checklist)

These are the **non-negotiable deliverable expectations** from [prd.md](prd.md). They stay in this file so the log and the “what done means” bar stay in one place; **full wording, traceability, and acceptance criteria** remain in the PRD and [todo.md](todo.md).

#### Functional (summary)

| Area | What the system must satisfy |
|------|------------------------------|
| **Crew & skills** | CrewAI crew with distinct roles (research, outline/architect, writer, figure/graph, LaTeX builder, compilation, QA). Domain knowledge in **Skills** (`SKILL.md` packages); operations via **Tools**. Per-agent / crew / programmatic skill loading as in FR-2–FR-4. |
| **Inputs** | User provides **topic** and **language** (e.g. English or Hebrew). |
| **Authoring** | **Markdown-first** chapters, then conversion to `.tex`. Final PDF **15–20 pages**. **TOC**, chapters/sections, **headers/footers**. |
| **Required elements** | At least one each: **diagram**, **image**, **Python-generated graph** (saved to disk, correct paths in `.tex`), **table**, **decorated math** (not plain text). |
| **Cover & layout** | **Thematic cover**: title, author, date, language. |
| **BiDi** | At least one chapter with **correct RTL↔LTR** (Hebrew + embedded English/technical terms). For Hebrew target language, **document-wide RTL** (TOC, headers, captions, numbering) correct per FR-14. |
| **Bibliography** | Sources in **`.bib`**; **BibTeX/biber**; in-text citations **linked** to bibliography entries. |
| **Compilation** | **MiKTeX**; **LuaLaTeX** (preferred) or **XeLaTeX**. **Multi-pass** pipeline (engine → bib → additional engine passes) until references resolve. **Clear diagnostics** on failure (logs, failing pass). |
| **QA** | Verify links, citations, TOC/lists, formulas typeset correctly, and related contract items (FR-20). |

#### Non-functional (always relevant)

- **Secrets:** API keys and tunables from environment / `.env`; never hard-coded or logged (NFR-9).
- **Reproducibility / clarity:** Same config + seed should yield a repeatable pipeline where the stack allows; generated `.tex` / `.bib` human-readable (NFR-3, NFR-10).
- **Observability:** Stages log inputs/outputs to the structured working tree (NFR-8).
- **i18n:** Unicode + BiDi via LuaLaTeX/XeLaTeX and appropriate fonts (NFR-7).

**Definition of Done (one line):** One run produces a compliant **15–20 page PDF** with cover, TOC, required media and math, a BiDi-demonstration chapter, linked bibliography, and clean multi-pass build—see [prd.md](prd.md) §9 for the full acceptance checklist.

### Python modules (file length & layout)

Guidelines for **this repo’s `.py` files** (complements [plan.md](plan.md) §1.4 `scripts/` for one-off figure code):

| Guideline | Detail |
|-----------|--------|
| **Soft size limit** | Treat **~250–350 lines per module** as a review trigger—not a hard law. If a file keeps growing, **split by responsibility** (e.g. `compile_tex.py`, `crew.py`, `agents/writer.py`) rather than one “god file.” Align tighter (~150 LOC) with [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) when practical. |
| **Entry point** | Keep [main.py](main.py) **thin** (delegates to `articlebook.cli`). Core logic lives under `src/articlebook/`. |
| **Crew wiring** | Prefer **one module per concern** (`crew/agents.py`, `crew/tasks.py`, `crew/crew_builder.py`, `crew/workspace_tools.py`) so each file stays skimmable and maps to roles in the PRD. |
| **Tools & I/O** | Subprocess (LaTeX), path helpers, and retries belong in **dedicated helpers**, not duplicated across agents. |
| **`scripts/`** | Figure/diagram scripts should stay **short and single-purpose** (generate one asset, exit); complex plotting logic can import a tiny shared `scripts/lib/` if needed. |

**Rationale:** Shorter files reduce merge/review friction, match the “single-responsibility” agent story in the PRD, and make it easier for humans (and LLMs) to load only the context they need.

---

## How to append a prompt entry

Use this pattern for each new logged interaction:

| Field | Content |
|-------|---------|
| **Tool** | e.g. Cursor Agent, CLI |
| **Date** | ISO-style date |
| **Context** | Repo state / milestone |
| **Prompt summary** | Short quote or paraphrase |
| **Purpose** | Why the prompt was run |
| **Output summary** | Files, features, docs |
| **Key decisions** | Bullets |
| **Lessons learned** | Bullets |

---

## Best practices

### Cross-project (from HW1–HW2 and general practice)

1. **Documentation before heavy code:** PRD → plan → backlog → implementation reduces rework; for LLM systems, written **contracts** (schemas, checklists, artifact layout) anchor tests and reviews.
2. **Config and secrets via environment:** Tunables and API keys from env / `.env`, not hard-coded or logged (see [prd.md](prd.md) NFR-9 and [config.py](config.py)).
3. **Reproducibility:** Fixed **seeds** and pinned or recorded dependency versions where the stack allows (this project exposes `SEED` for future use; record LaTeX/Python package versions in `versions.txt` per backlog).
4. **Centralized guards:** A “Gatekeeper”-style layer for file I/O (HW1) or API/token limits (HW2) generalizes to **one place** for retries, caps, and logging—use the same idea for LLM calls and LaTeX subprocesses as the crew grows.
5. **Tests tied to real failure modes:** HW2 added chaos/recovery and network-fault tests; HW3 should add compilation, citation, and artifact-path checks per [todo.md](todo.md) Phase M6.

### HW3-specific

1. **Skills per agent:** Keep prompts maintainable—instruction lives in `skills/`, not only inline strings ([plan.md](plan.md) §1.3).
2. **Artifact layout:** Use the planned tree (`content/`, `figures/`, `latex/`, `build/`) so agents and compilers share one contract ([plan.md](plan.md) §1.4).
3. **LaTeX pipeline:** Prefer **multi-pass** engine + biber/bibtex until references settle; surface log excerpts on failure ([prd.md](prd.md) FR-18, FR-19).
4. **BiDi and Unicode:** LuaLaTeX/XeLaTeX with Hebrew-capable fonts and explicit RTL/LTR segments where required ([prd.md](prd.md) FR-13, FR-14).

---

## Prior coursework (HW1–HW2)

Earlier homework used this file as a **long** step-by-step log (neural signal extraction, then multi-process **Judge / Pro / Con** debate with JSON pipe IPC, token **Gatekeeper**, **Watchdog** respawn, search cache, and Phase 9 chaos/security tests). That narrative lived in **PROMPTS.md v2.00**; it is **not** reproduced here to avoid bloating the HW3 repo. Retrieve it from **git history** (`PROMPTS.md` before the HW3 rewrite) if you need verbatim entries.

**Axis comparison (condensed):**

| Axis | HW1 (signals) | HW2 (debate) | HW3 (this repo) |
|------|-----------------|--------------|------------------|
| Compute primitive | PyTorch (MLP/RNN/LSTM) | LLM + tools (search) | CrewAI + LLM tools + LaTeX |
| Concurrency | Single-process training | Parent + 2 children (IPC) | Target: pipeline + compile subprocess(es) |
| Guard / safety | File I/O gatekeeper | Token/RPM caps, watchdog | Env keys, future caps on LLM/tool calls |
| Output artifact | Predictions + plots | Transcript + verdict JSON | PDF + Markdown / `.tex` / `.bib` |
| External dependency | None (data synthetic) | LLM + search | LLM + MiKTeX (+ optional search tools) |

---

## HW3 prompt log

### Prompt 1 — Documentation and M0 scaffolding

**Tool:** AI-assisted (architecture / documentation pass)  
**Date:** 2026-05-30 (per [prd.md](prd.md) / [plan.md](plan.md) headers)

**Context:** New HW3 scope: multi-agent book/article generation with CrewAI and LaTeX per assignment requirements.

**Prompt summary:** Produce product requirements, implementation plan, phased backlog, minimal runnable LaTeX path, and Python entrypoint.

**Purpose:** Lock requirements and milestone exit criteria before wiring the full crew.

**Output summary:**

- [prd.md](prd.md) — functional/non-functional requirements, user stories, Crew + Skills + LaTeX pipeline.
- [plan.md](plan.md) — architecture diagram, agent table, skills layout, stack, phases M0–M6.
- [todo.md](todo.md) — granular tasks with FR/NFR traceability.
- [main.py](main.py), [config.py](config.py), [requirements.txt](requirements.txt), [README.md](README.md) — CLI stub, env-based config, dependencies, usage blurb.
- LaTeX skeleton under `latex/` and compile output under `build/` (per M0 in [todo.md](todo.md)).

**Key decisions:**

- Markdown-first authoring, then LaTeX build and QA loop ([plan.md](plan.md) §1).
- LuaLaTeX primary; MiKTeX-oriented Windows path helper in [main.py](main.py).

**Lessons learned:**

- Treat PRD/plan/todo as the **contract** for what “done” means before expanding code.

---

### Prompt 2 — PROMPTS.md reframed for HW3

**Tool:** Cursor Agent  
**Date:** 2026-05-31

**Context:** [PROMPTS.md](PROMPTS.md) still described HW1/HW2; repo is HW3.

**Prompt summary:** Update PROMPTS.md for this project; keep purpose and important lessons; follow agreed plan (snapshot, best practices, compressed prior work, HW3 log).

**Purpose:** Single source of truth for AI-assisted work **on this repository**.

**Output summary:** File at **v3.00** — HW3 snapshot, append template, merged best practices, short HW1–HW2 pointer + axis table, HW3 prompt entries.

**Key decisions:**

- Supersede long HW1/HW2 prompt bodies; **preserve** purpose, practices, and **one-line** pointer to git for full legacy log.

**Lessons learned:**

- When reusing a prompts log across courses, **version and scope** the header so newcomers are not misled by old homework content.

---

### Prompt 3 — Snapshot accuracy pass (v3.01)

**Tool:** Cursor Agent  
**Date:** 2026-05-31

**Context:** Repo gained `content/`, `figures/`, `scripts/`, `versions.txt`, local `.env` (gitignored), and `requirements.txt` uses `>=` minimums; `skills/` not yet created.

**Prompt summary:** Update prompts.md for this project; keep the important things.

**Purpose:** Keep the development log aligned with the tree and dependencies without dropping purpose, template, practices, or prior entries.

**Output summary:**

- [PROMPTS.md](PROMPTS.md) **v3.01** — filename note, corrected dependency wording, env / `versions.txt` / layout bullets, explicit “skills folder pending M1,” preserved sections above.

**Key decisions:**

- Prefer **accurate snapshot** over aspirational file paths; still point to [plan.md](plan.md) for the full skills layout.

**Lessons learned:**

- Re-read `requirements.txt` and the directory tree when describing “pins” vs minimum versions.

---

### Prompt 4 — Restore general requirements in PROMPTS.md

**Tool:** Cursor Agent  
**Date:** 2026-05-31

**Context:** [PROMPTS.md](PROMPTS.md) v3.01 had snapshot and practices but no condensed PRD/assignment checklist in-file.

**Prompt summary:** Keep the general requirements (in addition to the rest of the doc).

**Purpose:** Readers of this log should see the **deliverable contract** without opening [prd.md](prd.md) first.

**Output summary:**

- [PROMPTS.md](PROMPTS.md) **v3.02** — new **General requirements (assignment / PRD contract)** section: functional summary table, key NFR bullets, one-line DoD pointer to PRD §9.

**Key decisions:**

- **Summarize** FR/NFR in a table; defer verbatim requirements and task mapping to [prd.md](prd.md) and [todo.md](todo.md).

**Lessons learned:**

- A prompts log for coursework doubles as a **quick compliance checklist** if the general requirements stay visible.

---

### Prompt 5 — General requirements = Python file length guidance

**Tool:** Cursor Agent  
**Date:** 2026-05-31

**Context:** “General requirements” was intended to include **how long `.py` files should be**, not only the PRD checklist.

**Prompt summary:** Keep requirements like the length of Python files.

**Purpose:** Encode **module size and layout** expectations next to the assignment checklist so implementation stays maintainable.

**Output summary:**

- [PROMPTS.md](PROMPTS.md) **v3.03** — **General requirements** is an umbrella section: **Assignment / PRD** (renamed subsections) plus **Python modules (file length & layout)** table (~250–350 line soft limit, thin `main.py`, split crew/agents/tools, short `scripts/`).

**Key decisions:**

- Use a **soft line-count band** plus **split-by-responsibility** rule instead of an arbitrary hard cap.

**Lessons learned:**

- In shared logs, label **“assignment vs codebase conventions”** explicitly when both are called “requirements.”

---

### Prompt 6 — Milestone M1 (skills, agents, crew, uv)

**Tool:** Cursor Agent  
**Date:** 2026-05-31

**Context:** `plan.md` / `todo.md` Phase M1 exit criteria: skills packages, agent roster, sequential crew, shared working directory, stub dry run.

**Prompt summary:** Execute phase 1 with a professional implementation following engineering instructions.

**Purpose:** Land M1 so later milestones can focus on content, figures, LaTeX assembly, and multi-pass compile without re-plumbing orchestration.

**Output summary:**

- `skills/**/SKILL.md` — eight packages (`house-culture` crew default + seven specialist skills).
- `src/articlebook/` — `cli`, `pipeline`, `crew/*`, `shared/{config,gatekeeper,paths}`, `skills_inventory.py`, `__main__.py`.
- `pyproject.toml` + `uv.lock`, dev tools (`ruff`, `pytest`), console script `articlebook`.
- `scripts/plot_stub_m1.py` — deterministic Matplotlib PDF for the figure agent / stub path.
- `docs/PRD_m1_crew_and_skills.md` — mechanism PRD for M1 wiring and operational modes.
- `tests/` — YAML front matter checks, stub pipeline artifacts, workspace sandbox tests.
- `README.md`, `todo.md` (M1 tasks checked), `PROMPTS.md` snapshot refresh.

**Key decisions:**

- **Gatekeeper** owns `LLM` construction; workspace tools use a **ContextVar**-bound repo root (documented risk if tools ever run off-thread).
- **`--stub`** path guarantees CI-friendly artifacts without API keys; missing `lualatex` writes a skip log instead of failing tests.

**Lessons learned:**

- Bind filesystem tools to an explicit root and **whitelist** reads when exposing repo-level docs to agents.

---

### 2026-05-31 — Milestone M2 (content pipeline)

**Goal:** Implement `plan.md` / `todo.md` Phase M2 — outline with page budgets, multi-file Markdown, BiDi chapter, `.bib`, validated inputs.

**Changes (summary):**

- `articlebook.inputs` — `RunInputs`, `validate_topic_language`, `normalize_text_direction`, structured run logging.
- `articlebook.m2_stub` — deterministic `content/` + `latex/references.bib` + `build/m2_stub_manifest.md`.
- `articlebook.pipeline` — `run_stub_m2`, `run_llm(..., milestone=)`, retained `run_stub_m1` / `run_llm_m1`.
- `crew.tasks.build_m2_tasks`, `crew_builder.build_crew` / `build_m2_crew`; CLI `--milestone {m1,m2}` (default **m2**).
- Docs: `docs/PRD_m2_content_pipeline.md`, README usage, `todo.md` / `SYSTEM_PROMPT.md` / `PROMPTS.md` updates.

**Key decisions:**

- **Default milestone m2** for new runs; M1 retained for regression and full smoke.
- **M2 LLM crew is truncated** (4 agents) so milestone scope stays content-only; compile returns in M1 or later milestones.

---

### 2026-05-31 — Milestone M4 (LaTeX assembly)

**Goal:** `plan.md` / `todo.md` Phase M4 — assemble compilable `main.tex`, map Markdown chapters to `latex/chapters/*.tex`, preamble (FR-8, FR-12, FR-15–FR-16).

**Changes (summary):**

- `articlebook.m4_assembly` — Markdown subset → TeX, `write_main_tex`, manifests.
- `assemble_latex_document` + extended `run_lualatex_once(log_filename=...)` in `workspace_tools`.
- `build_m4_tasks`, `run_stub_m4`, CLI `--milestone m4`, `docs/PRD_m4_latex_assembly.md`, tests.

**Key decisions:**

- **English `\setdefaultlanguage`** + `hebrew` as `otherlanguage` for predictable first-pass builds; Hebrew-primary PDF deferred.
- **biblatex** before **hyperref** before **cleveref**; one LuaLaTeX pass (M5 adds biber loop).

---

### 2026-06-01 — Milestone M7 (Phase 7 — production harness, gatekeeper, YAML config)

**Goal:** `plan.md` §11 / `todo.md` §M7 — externalize model + gatekeeper settings; wrap LLM calls with retries/backoff/timeout/rate-limit knobs; optional agent/task overlays; compilation skill; keep `--stub` + CLI stable.

**Changes (summary):**

- `config/models.yaml`, `config/agents.yaml`, `config/tasks.yaml` + `articlebook.shared.config_paths`, expanded `shared/config.py` (`load_models_document`, `write_resolved_run_stamp`).
- `articlebook.shared.gatekeeper` — `InstrumentedLLM` subclass (transient-error retries + jitter, per-call latency + token-delta + rough USD estimate from YAML pricing table).
- `articlebook.crew.agent_overrides`, `articlebook.crew.task_overrides`; `crew/agents.py` merges YAML; `tasks_m2.py` uses task overrides; `skills/compilation/SKILL.md`.
- `pipeline.run_llm` — stamp `build/resolved_run_config.json`, richer `log_resolved_run_config`, lenient output validation in `task_callback`, post-kickoff `get_token_usage_summary` log.
- Docs/tests: `docs/PRD_m7_production_harness.md`, `tests/test_m7_gatekeeper_policy.py`, `tests/test_m7_config_yaml.py`, `SYSTEM_PROMPT.md` / `todo.md` / `handoff.md` / `README.md` / `pyproject.toml` sdist `config/`.

**Key decisions:**

- **Subclass `crewai.LLM`** rather than monkey-patching LiteLLM — keeps CrewAI events/hooks intact while centralizing policy.
- **Tools stay code-defined**; YAML only adjusts agent copy + skill folder list + optional M2 task prompt overrides (`{topic}` / `{language}`).

---

### Next entries (suggested)

- **M8–M9:** Security guards + approval gate; structured `run_report` JSON/Markdown.

Record each as a new subsection under **HW3 prompt log** using the template above.
