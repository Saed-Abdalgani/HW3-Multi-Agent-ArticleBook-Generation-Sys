# Multi-Agent Article/Book Generation System

Generate a 15–20 page LaTeX book/article using **CrewAI** (see `prd.md`, `plan.md`, `todo.md`).

## Requirements

- **Python** 3.11–3.13 (see `pyproject.toml`)
- **uv** for environments and commands ([https://docs.astral.sh/uv/](https://docs.astral.sh/uv/))
- **MiKTeX** (Windows) with `lualatex` and **`biber`** on `PATH` for real multi-pass builds (optional for `--stub` when the engine is missing; the driver still writes a skip journal)
- **OpenAI API key** in the environment for LLM crew runs (not required for `--stub`)

## Install

```bash
uv sync --all-groups
```

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (never commit `.env`).

Optional: set **`ARTICLEBOOK_LATEX_ENGINE=xelatex`** if LuaLaTeX is unavailable but XeLaTeX works.

## Usage

**Offline stub — M2 content pipeline (default):** outline, six chapters (including BiDi), `references.bib`, research notes, review gate (no LLM, no LaTeX required):

```bash
uv run articlebook --stub --topic "Your Topic" --language English
```

**Offline stub — M1 full smoke** (placeholder artifacts, Matplotlib stub, optional LuaLaTeX once):

```bash
uv run articlebook --stub --milestone m1 --topic "Your Topic" --language English
```

**Offline stub — M3** (everything in M2 plus `scripts/make_graph.py` / `make_image.py`, `figures/graph.pdf`, `figures/image.png`, and `build/m3_stub_manifest.md`; LaTeX showcase is `latex/chapters/m3_fr9_showcase.tex` included from `latex/main.tex`):

```bash
uv run articlebook --stub --milestone m3 --topic "Your Topic" --language English
```

**Offline stub — M4** (M2 + M3, Markdown → `latex/chapters/*.tex`, regenerated `main.tex`, then **canonical multipass compile**: engine → **biber** → engine ×2+ with stabilization, per `plan.md` §4). Logs and `build/m4_compile_journal.json`:

```bash
uv run articlebook --stub --milestone m4 --topic "Your Topic" --language English
```

**Offline stub — M5** (same pipeline as M4 stub; writes `build/m5_stub_manifest.md` and `build/m5_compile_journal.json` for M5 sign-off trail):

```bash
uv run articlebook --stub --milestone m5 --topic "Your Topic" --language English
```

**LLM crew** — requires `OPENAI_API_KEY`. Default is **M2** (research → outline → chapters → QA). Milestones:

- `m1` — full-stack smoke (single `run_lualatex_once` in compile task)
- `m3` — M2 + figure generators + extended QA
- `m4` — M3 + LaTeX assembly + **one** compile pass in the crew task (legacy smoke)
- **`m5`** — M3 + LaTeX assembly + **`run_latex_canonical_compile`** (multipass + biber) + QA on compile journal

```bash
uv run articlebook --topic "Your Topic" --language Hebrew
uv run articlebook --milestone m1 --topic "Your Topic" --language English
uv run articlebook --milestone m3 --topic "Your Topic" --language English
uv run articlebook --milestone m4 --topic "Your Topic" --language English
uv run articlebook --milestone m5 --topic "Your Topic" --language English
```

Legacy entrypoint:

```bash
uv run python main.py --stub --topic "Your Topic" --language English
```

## M5 compile artifacts

Under `build/` (prefix from stub `m4`/`m5` or crew `m5_crew`):

- `*_passNN_*.log` — stdout/stderr per subprocess
- `*_compile_journal.json` — pass list, return codes, unresolved log line samples
- `*_failure.txt` — tail excerpt when a pass fails (plus `error_class`)

Mechanism PRD: [`docs/PRD_m5_compile.md`](docs/PRD_m5_compile.md).

## Layout

- `src/articlebook/` — library: CLI, pipeline, CrewAI crew, `latex_compile/` (multipass driver; `compile_multipass.py` re-exports), workspace tools, gatekeeper LLM factory
- `skills/` — CrewAI `SKILL.md` packages (per-agent + `house-culture` at crew level)
- `content/`, `figures/`, `scripts/`, `latex/`, `build/` — working tree for generated artifacts
- `docs/PRD_m1_crew_and_skills.md` — mechanism PRD for milestone M1 wiring
- `docs/PRD_m4_latex_assembly.md` — mechanism PRD for M4 Markdown→TeX and `main.tex` assembly
- `docs/PRD_m5_compile.md` — multipass + biber driver
- `handoff.md` — short pointer for the next agent session

## Development

```bash
uv run ruff check src tests
uv run pytest
```

## Troubleshooting

- **`OPENAI_API_KEY is not set`:** use `--stub`, or export the key before running the LLM path.
- **`lualatex not found`:** install MiKTeX and ensure `lualatex` / `biber` are on `PATH` (on Windows the driver also prepends the default MiKTeX user `bin` when engines are missing from `PATH`).
- **Want XeLaTeX instead:** set `ARTICLEBOOK_LATEX_ENGINE=xelatex` in the environment.
- **Import errors running `python main.py` outside `uv`:** run via `uv run` so the `articlebook` package from `src/` is on the environment path.

## Credits / license

Coursework (HW3). Add license terms when publishing beyond the classroom.
