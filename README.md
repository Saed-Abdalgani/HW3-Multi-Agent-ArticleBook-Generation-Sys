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

**Offline stub pipeline** (writes M1 placeholder artifacts, runs Matplotlib stub, skips or smoke-runs LaTeX):

```bash
uv run articlebook --stub --topic "Your Topic" --language English
```

**LLM crew (sequential M1 tasks)** — requires `OPENAI_API_KEY`:

```bash
uv run articlebook --topic "Your Topic" --language Hebrew
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
