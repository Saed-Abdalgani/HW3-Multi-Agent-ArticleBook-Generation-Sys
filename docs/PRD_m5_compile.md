# Mechanism PRD — M5 LaTeX compilation & link resolution

| Field | Value |
|-------|-------|
| Related | `prd.md` FR-15–FR-19, `plan.md` §4 |
| Implementation | `src/articlebook/latex_compile/` (+ shim `compile_multipass.py`); tool `run_latex_canonical_compile` |

## Canonical sequence

1. `lualatex` or `xelatex` (`ARTICLEBOOK_LATEX_ENGINE`) on `latex/main.tex` with `-output-directory=build/`.
2. `biber main` with `cwd=build/` (job name `main`).
3. Two mandatory engine passes.
4. Up to four additional passes while `main.log` still requests reruns (undefined cites, TOC, etc.).

## Artifacts

- Per-pass logs: `build/<prefix>_passNN_*.log`
- Journal: `build/<prefix>_compile_journal.json` (exit codes, commands, unresolved line samples)
- Failure excerpt: `build/<prefix>_failure.txt` when a subprocess fails

## Configuration

- `ARTICLEBOOK_LATEX_ENGINE`: `lualatex` (default) or `xelatex`.

## Crew / stub wiring

- Stub M4/M5: `compile_latex_canonical` after assembly (`pipeline_stubs._stub_latex_through_m5_driver`).
- LLM M5: `run_latex_canonical_compile(log_prefix="m5_crew")` in `tasks_m5.py`.

## M6 follow-up

Automated QA over journal + PDF (page count, `??`, FR-9 audit) remains milestone M6.
