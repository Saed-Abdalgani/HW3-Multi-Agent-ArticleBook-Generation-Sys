# Handoff (post M7)

## Status

**M7 done:** `config/{models,agents,tasks}.yaml` + `shared/config.py` merge; **`InstrumentedLLM`** (retries/backoff, timeout, optional min interval, per-call latency + token delta + rough USD estimate); **`build/resolved_run_config.json`** stamp; **`skills/compilation/SKILL.md`** on the Compilation agent; M2 tasks honor **`tasks.yaml`** overrides; tests in `tests/test_m7_gatekeeper_policy.py` + `tests/test_m7_config_yaml.py`.

**Still NOT READY for full DoD:** **M6** manual BiDi PDF + MiKTeX run without `--m6-allow-missing-pdf` (see `prd.md` §9). **M8–M9** (security gate, run reports) remain open per `plan.md` §11.

## Key files (read these first)

| Area | Path |
|------|------|
| M7 config | `config/models.yaml`, `config/agents.yaml`, `config/tasks.yaml`; loaders `shared/config.py`, `shared/config_paths.py`, `crew/agent_overrides.py`, `crew/task_overrides.py` |
| Gatekeeper | `src/articlebook/shared/gatekeeper.py` (`InstrumentedLLM`, `create_llm`) |
| Driver | `src/articlebook/latex_compile/` (`canonical.py`, `runner.py`, …); shim `compile_multipass.py` |
| Crew tool | `src/articlebook/crew/workspace_tools.py` → `run_latex_canonical_compile` |
| M5/M6 tasks | `src/articlebook/crew/tasks_m5.py`, `tasks_m6.py`, `crew_builder.py` |
| Deterministic fixtures (tests / scripts) | `src/articlebook/pipeline_stubs.py` (`run_stub_m4` … `run_stub_m6`) — not exposed on CLI |
| Spec | `docs/PRD_m5_compile.md`, `docs/PRD_m6_qa_contract.md`, `docs/PRD_m7_production_harness.md`, `plan.md` §4 / §11 |

## Env

- `ARTICLEBOOK_LATEX_ENGINE` = `lualatex` (default) or `xelatex` (see README env table).
- `ARTICLEBOOK_CONFIG_DIR` — optional alternate directory for `models.yaml` / `agents.yaml` / `tasks.yaml`.

## Artifacts

`build/<prefix>_pass*.log`, `build/<prefix>_compile_journal.json`, optional `*_failure.txt`, `*_biber_warning_excerpt.txt`, **`build/resolved_run_config.json`** (M7 LLM stamp).

## Next agent (M8)

1. Implement `shared/security.py`, `--dry-run` / `--yes`, overwrite guards per `todo.md` §M8 + `plan.md` §10.3.
2. Add `skills/security-review/SKILL.md` and red-team tests.
3. Update `SYSTEM_PROMPT.md` Missing table when M8 closes.
