# Multi-Agent Article/Book Generation System

Generate a 15–20 page LaTeX book/article using **CrewAI** (see `prd.md`, `plan.md`, `todo.md`).

## Requirements

- **Python** 3.11–3.13 (see `pyproject.toml`)
- **uv** for environments and commands ([https://docs.astral.sh/uv/](https://docs.astral.sh/uv/))
- **MiKTeX** (Windows) with `lualatex` on `PATH` for real compiles (optional for `--stub` CI runs)
- **OpenAI API key** in the environment for LLM crew runs (not required for `--stub`)

## Install

```bash
uv sync --all-groups
```

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (never commit `.env`).

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

**Offline stub — M4** (M2 + M3 binaries, then **Markdown → `latex/chapters/*.tex`**, regenerated `latex/main.tex` with biblatex/hyperref/cleveref/fancyhdr/polyglossia, one LuaLaTeX pass logged to `build/m4_lualatex_once.log`):

```bash
uv run articlebook --stub --milestone m4 --topic "Your Topic" --language English
```

**LLM crew** — requires `OPENAI_API_KEY`. Default is **M2** (research → outline → chapters → QA). Use `--milestone m1` for the original full-stack crew, **`m3`** for M2 + figure generators + extended QA, or **`m4`** for M3 + LaTeX assembly + compile + QA:

```bash
uv run articlebook --topic "Your Topic" --language Hebrew
uv run articlebook --milestone m1 --topic "Your Topic" --language English
uv run articlebook --milestone m3 --topic "Your Topic" --language English
uv run articlebook --milestone m4 --topic "Your Topic" --language English
```

Legacy entrypoint:

```bash
uv run python main.py --stub --topic "Your Topic" --language English
```

## Layout

- `src/articlebook/` — library: CLI, pipeline, CrewAI crew, workspace tools, gatekeeper LLM factory
- `skills/` — CrewAI `SKILL.md` packages (per-agent + `house-culture` at crew level)
- `content/`, `figures/`, `scripts/`, `latex/`, `build/` — working tree for generated artifacts
- `docs/PRD_m1_crew_and_skills.md` — mechanism PRD for milestone M1 wiring
- `docs/PRD_m4_latex_assembly.md` — mechanism PRD for M4 Markdown→TeX and `main.tex` assembly

## Development

```bash
uv run ruff check src tests
uv run pytest
```

## Troubleshooting

- **`OPENAI_API_KEY is not set`:** use `--stub`, or export the key before running the LLM path.
- **`lualatex not found`:** install MiKTeX and ensure `lualatex` is on `PATH` (on Windows the workspace tools also probe the default MiKTeX user install path).
- **Import errors running `python main.py` outside `uv`:** run via `uv run` so the `articlebook` package from `src/` is on the environment path.

## Credits / license

Coursework (HW3). Add license terms when publishing beyond the classroom.
