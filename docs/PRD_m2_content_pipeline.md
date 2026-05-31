# PRD — Milestone M2 content pipeline

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Implemented (stub + LLM crew) |
| Related | `prd.md` FR-5–FR-8, FR-13–FR-16; `plan.md` Phase M2; `todo.md` §M2 |

---

## 1. Purpose

Deliver a **reviewable Markdown-first book draft** with a **15–20 page estimate**, **per-chapter budgets**, a dedicated **BiDi chapter**, stable **asset anchors** for downstream LaTeX, and a **`references.bib`** corpus whose keys match **in-text citation markers**—without requiring M3–M5 tooling.

---

## 2. Inputs

| Input | Validation | Derived |
|-------|--------------|---------|
| `topic` | Non-empty, max length, no newlines/NUL | Echoed in artifacts |
| `language` | Non-empty, max length | `text_direction`: RTL if Hebrew (incl. `עברית`, `he`, `iw`), else LTR |

Implementation: `articlebook.inputs.validate_topic_language`, `log_resolved_run_config`.

---

## 3. Modes

### 3.1 Stub (`--stub`, default `--milestone m2`)

Deterministic writer: `articlebook.m2_stub.write_m2_stub_artifacts`.

- No LLM, no network, suitable for CI.
- Emits curated **real-style** BibTeX (Knuth, Lamport, CrewAI docs, Markdown Guide, placeholder journal article).
- Page heuristic: **~250 words/page**; outline totals **~17 pages** of budgeted content.

### 3.2 LLM (`build_crew(..., milestone="m2")`)

Sequential crew: **Research → Architect → Writer → QA** (no figure/latex/compile agents).

Tasks: `articlebook.crew.tasks.build_m2_tasks`.

---

## 4. Artifact contract

| Path | Owner (conceptual) | Requirement |
|------|-------------------|---------------|
| `content/research_notes.md` | Research | Sources + citation hygiene notes |
| `latex/references.bib` | Research | Valid BibTeX; keys cited in chapters |
| `content/outline.md` | Architect | Table: pages + words per chapter; BiDi row; asset anchor list |
| `content/chapter_01_scope.md` … `chapter_06_conclusion.md` | Writer | Separate files; `[@citekey]` markers; HTML comment anchors |
| `content/chapter_04_bidi_technical_note.md` | Writer | RTL Hebrew + LTR islands **or** English + RTL block quote demo |
| `content/REVIEW_GATE.md` | Writer | Human approval before M4 |
| `build/m2_qa_report.md` | QA (LLM only) | Checklist (stub writes `m2_stub_manifest.md` instead) |

Citation style in Markdown: **pandoc**-style `[@bibkey]` for forward compatibility with M4 conversion.

---

## 5. Non-goals (M2)

- PDF page proof, diagrams, Matplotlib output, multi-pass LaTeX (M3–M5).
- Automated verification that LLM output is factually correct (human + M6 QA).

---

## 6. Testing

- `tests/test_inputs.py` — validation + RTL mapping.
- `tests/test_stub_pipeline.py` — `run_stub_m2` writes outline, BiDi chapter, `.bib`.

---

## 7. CLI

```bash
uv run articlebook --stub --topic "My Topic" --language Hebrew   # default M2
uv run articlebook --stub --milestone m1 --topic "T" --language English
uv run articlebook --topic "My Topic" --language English         # LLM M2
```
