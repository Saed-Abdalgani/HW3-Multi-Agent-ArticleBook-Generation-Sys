# Handoff (post M5)

## Status

**M5 done:** canonical compile driver (`compile_latex_canonical`), Crew tool `run_latex_canonical_compile`, stub **`--milestone m4|m5`** both run assembly + multipass; LLM **`--milestone m5`** uses `tasks_m5.py` (multipass + QA on journal).

**Still NOT READY:** **M6** (FR-20 QA contract, 15–20 page PDF check, BiDi visual proof, DoD in `prd.md` §9).

## Key files (read these first)

| Area | Path |
|------|------|
| Driver | `src/articlebook/latex_compile/` (`canonical.py`, `runner.py`, …); shim `compile_multipass.py` |
| Crew tool | `src/articlebook/crew/workspace_tools.py` → `run_latex_canonical_compile` |
| M5 tasks | `src/articlebook/crew/tasks_m5.py`, `crew_builder.py` (`milestone="m5"`) |
| Stubs | `src/articlebook/pipeline_stubs.py` (`run_stub_m4`, `run_stub_m5`) |
| Spec | `docs/PRD_m5_compile.md`, `plan.md` §4 |

## Env

- `ARTICLEBOOK_LATEX_ENGINE` = `lualatex` (default) or `xelatex` (`.env.example`).

## Artifacts

`build/<prefix>_pass*.log`, `build/<prefix>_compile_journal.json`, optional `*_failure.txt`, `*_biber_warning_excerpt.txt`.

## Next agent (M6)

1. Implement automated checks from `todo.md` §M6 + `skills/qa-checklist/SKILL.md` (log/PDF parsing as feasible).
2. Wire QA task to consume `*_compile_journal.json` + `main.log` without re-reading entire repos.
3. Update `SYSTEM_PROMPT.md` Missing table when M6 closes.
