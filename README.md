# Multi-Agent Article/Book Generation System

Generate a 15–20 page LaTeX book/article using **CrewAI** (see `prd.md`, `plan.md`, `todo.md`).

## Requirements

- **Python** 3.11–3.13 (see `pyproject.toml`)
- **uv** for environments and commands ([https://docs.astral.sh/uv/](https://docs.astral.sh/uv/))
- **`litellm`** (declared in `pyproject.toml`) — required for the **instrumented** gatekeeper LLM path (retries, multi-key failover, usage logs). CrewAI may use the native OpenAI SDK for non-instrumented `LLM` construction.
- **MiKTeX** (Windows) with `lualatex` and **`biber`** on `PATH` for real multi-pass builds (without them, the compile driver still writes journals; M6 can use `--m6-allow-missing-pdf` for static QA only)
- **LLM API keys** — either legacy vars (`OPENAI_API_KEY` / `GOOGLE_API_KEY` / …) **or** a single **`ARTICLEBOOK_LLM_ROUTES`** line for mixed OpenRouter/Groq/NVIDIA (see env table). When routes are set, the resolved **`provider` is always `openai`** (LiteLLM); real upstreams follow each slot’s model prefix.

## Install

```bash
uv sync --all-groups
```

Create a **`.env`** file in the repo root (gitignored — never commit it). Copy **`.env_example`** to `.env` and fill in your keys. See **Environment variables** below.

### Environment variables (local `.env` only)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Primary OpenAI key (always used first on each LLM call when set). |
| `OPENAI_API_KEY_2`, `OPENAI_API_KEY_3` | Optional extra OpenAI keys: on HTTP rate-limit style errors, the gatekeeper switches to the next key in order before backoff. |
| `GOOGLE_API_KEY` or `GEMINI_API_KEY` | Primary Google Gemini key (first in chain for that family). |
| `GOOGLE_API_KEY_2`, `GOOGLE_API_KEY_3` (or `GEMINI_API_KEY_2`, `GEMINI_API_KEY_3`) | Optional failover keys for Google runs (same rotation behavior). |
| `MODEL_NAME`, `TEMPERATURE`, `SEED` | Overrides for `config/models.yaml` defaults. |
| `ARTICLEBOOK_LLM_PROVIDER` | e.g. `openai` or `google`. |
| `ARTICLEBOOK_LLM_TIMEOUT_S` | LLM timeout (seconds). |
| `ARTICLEBOOK_CONFIG_DIR` | Alternate directory for `config/*.yaml`. |
| `ARTICLEBOOK_OPENROUTER_KEY_SUFFIX` | With Groq + NVIDIA suffixes, builds routes automatically: paste only the part after `sk-or-v1-` (or the full key). |
| `ARTICLEBOOK_GROQ_KEY_SUFFIX` | Same for Groq: paste after `gsk_` or full `gsk_…` key. |
| `ARTICLEBOOK_NVIDIA_KEY_SUFFIX` | Same for NVIDIA: paste after `nvapi-` or full `nvapi-…` key. |
| `ARTICLEBOOK_ROUTE_MODELS` | Optional override: exactly **three** LiteLLM model ids separated by `;` (NVIDIA slot, OpenRouter slot, Groq slot). Defaults are set in code if unset. |
| `ARTICLEBOOK_LLM_ROUTES` | Advanced: explicit `key\|model;…` list (overrides suffix mode if non-empty). See **`.env_example`** for the simple triple-key layout. |
| `ARTICLEBOOK_GK_RETRY_MAX`, `ARTICLEBOOK_GK_MIN_INTERVAL_S` | Gatekeeper knobs. |
| `ARTICLEBOOK_RAG_ENABLED` | `true` / `1` to force RAG on (YAML is primary). |
| `ARTICLEBOOK_LATEX_ENGINE` | `lualatex` (default) or `xelatex`. |

### CI / tests without paid API calls

Deterministic workspace fixtures are produced by **`articlebook.pipeline_stubs`** (`run_stub_m2` … `run_stub_m6`). The pytest suite calls these modules directly; the **`articlebook` CLI no longer exposes `--stub`**.

### Multi-provider keys (OpenRouter + Groq + NVIDIA)

Copy **`.env_example`** to **`.env`** and fill in **`ARTICLEBOOK_OPENROUTER_KEY_SUFFIX`**, **`ARTICLEBOOK_GROQ_KEY_SUFFIX`**, and **`ARTICLEBOOK_NVIDIA_KEY_SUFFIX`** (secret after each vendor prefix, or paste the full key). The app prepends `sk-or-v1-`, `gsk_`, and `nvapi-` when needed and uses three default LiteLLM models (override with **`ARTICLEBOOK_ROUTE_MODELS`**).

Power users can still set **`ARTICLEBOOK_LLM_ROUTES`** to a full `key|model;…` string; if that variable is non-empty, it wins over the suffix shortcut.

### M7 — YAML config + Gatekeeper (Phase 7)

- **`config/models.yaml`** — provider, model defaults, `timeout_seconds`, `gatekeeper.*` retries/backoff/rate-limit knobs, `rag.enabled`, optional `pricing_per_million_tokens` for **rough** cost logs. Multi-key failover requires **`gatekeeper.instrumented: true`** (default): plain `LLM` construction does not rotate keys.
- **`config/agents.yaml`** — role/goal/backstory + skill folder names (tools stay code-defined).
- **`config/tasks.yaml`** — optional `overrides.<milestone>.<task_id>` for `description` / `expected_output` (M2 wired; `{topic}` / `{language}` placeholders supported).
- **`ARTICLEBOOK_CONFIG_DIR`** — point at an alternate config directory (see table above).
- Each LLM run writes **`build/resolved_run_config.json`** (redacted; no API keys).

Optional: set **`ARTICLEBOOK_LATEX_ENGINE=xelatex`** if LuaLaTeX is unavailable but XeLaTeX works.

## Usage

**LLM crew** — requires a configured API key (see above). Default milestone is **M2** (research → outline → chapters → QA).

```bash
uv run articlebook --topic "Your Topic" --language English
uv run articlebook --milestone m1 --topic "Your Topic" --language English
uv run articlebook --milestone m3 --topic "Your Topic" --language English
uv run articlebook --milestone m4 --topic "Your Topic" --language English
uv run articlebook --milestone m5 --topic "Your Topic" --language English
uv run articlebook --milestone m6 --topic "Your Topic" --language English
```

Milestones:

- `m1` — full-stack smoke (single `run_lualatex_once` in compile task)
- `m3` — M2 + figure generators + extended QA
- `m4` — M3 + LaTeX assembly + **one** compile pass in the crew task (legacy smoke)
- **`m5`** — M3 + LaTeX assembly + **`run_latex_canonical_compile`** (multipass + biber) + QA on compile journal
- **`m6`** — same as M5 crew tasks with `m6_crew` journal prefix + **`run_m6_contract_checks`**; CLI re-runs deterministic QA after kickoff and exits **1** on failure

On machines **without** MiKTeX, pass **`--m6-allow-missing-pdf`** so PDF/page checks and missing-engine compile status are relaxed (static checks still run; not a substitute for a real PDF sign-off).

**M8 (security):** paid runs prompt for confirmation unless you pass **`--yes`** (CI/automation). Use **`--dry-run`** to validate inputs and skip crew `write_workspace_file` bytes. If `content/` or `latex/` outputs already exist, you will be warned before overwrite unless `--yes` or `--dry-run`.

**M9 (observability):** each CLI run writes **`build/run_report_<run_id>.json`** and a matching **`.md`** (redacted task snippets, instrumented LLM rows, artifact flags). The CLI prints the paths when the run finishes.

**M9-OPT (local RAG, ADR-003):** set `rag.enabled: true` in `config/models.yaml` (or `ARTICLEBOOK_RAG_ENABLED=true`), install **`uv sync --extra rag`**, add corpus files under **`knowledge/`**, then the Research agent gets the **`retrieve_knowledge_snippets`** tool. Snippet `source_id` values map to `.bib` keys via Markdown front matter (`bib_key:`).

Legacy entrypoint:

```bash
uv run python main.py --topic "Your Topic" --language English
```

## M5 compile artifacts

Under `build/` (prefix from crew `m5_crew` or deterministic `pipeline_stubs` runs):

- `*_passNN_*.log` — stdout/stderr per subprocess
- `*_compile_journal.json` — pass list, return codes, unresolved log line samples
- `*_failure.txt` — tail excerpt when a pass fails (plus `error_class`)

Mechanism PRD: [`docs/PRD_m5_compile.md`](docs/PRD_m5_compile.md).

## M6 QA artifacts

- `build/m6_qa_report.md` / `build/m6_qa_report.json` — deterministic FR-20 contract (links/refs log scan, bib↔cite, FR-9, structure, PDF page band, secret scan)
- `build/m6_stub_manifest.md` — pointer after deterministic `run_stub_m6` (tests / fixtures)

Mechanism PRD: [`docs/PRD_m6_qa_contract.md`](docs/PRD_m6_qa_contract.md).

- `src/articlebook/` — library: CLI, pipeline, CrewAI crew, `latex_compile/` (multipass driver; `compile_multipass.py` re-exports), workspace tools, gatekeeper LLM factory
- `skills/` — CrewAI `SKILL.md` packages (per-agent + `house-culture` at crew level)
- `content/`, `figures/`, `scripts/`, `latex/`, `build/` — working tree for generated artifacts
- `docs/PRD_m1_crew_and_skills.md` — mechanism PRD for milestone M1 wiring
- `docs/PRD_m4_latex_assembly.md` — mechanism PRD for M4 Markdown→TeX and `main.tex` assembly
- `docs/PRD_m5_compile.md` — multipass + biber driver
- `docs/PRD_m6_qa_contract.md` — M6 deterministic QA contract (FR-20)
- `handoff.md` — short pointer for the next agent session

## Development

```bash
uv run ruff check src tests
uv run pytest
```

Optional local RAG (M9-OPT): `uv sync --extra rag` then enable `rag.enabled` in `config/models.yaml`.

## Troubleshooting

- **No LLM API key / wrong provider:** set `OPENAI_API_KEY` (and optionally `_2` / `_3` for failover) or `GOOGLE_API_KEY` / `GEMINI_API_KEY` to match `provider` in `config/models.yaml` (or override with `ARTICLEBOOK_LLM_PROVIDER`). For Gemini via LiteLLM/CrewAI, use a model id such as `gemini/gemini-2.0-flash` in `MODEL_NAME` or YAML.
- **`lualatex not found`:** install MiKTeX and ensure `lualatex` / `biber` are on `PATH` (on Windows the driver also prepends the default MiKTeX user `bin` when engines are missing from `PATH`).
- **Want XeLaTeX instead:** set `ARTICLEBOOK_LATEX_ENGINE=xelatex` in the environment.
- **Import errors running `python main.py` outside `uv`:** run via `uv run` so the `articlebook` package from `src/` is on the environment path.

## Credits / license

Coursework (HW3). Add license terms when publishing beyond the classroom.
