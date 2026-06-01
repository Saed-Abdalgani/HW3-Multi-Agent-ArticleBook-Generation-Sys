# PRD — M9 observability & run reporting

This document pins **Milestone M9** from `plan.md` §11 and `todo.md` Phase M9.

## Objectives

1. Assign a stable **`run_id`** per CLI invocation with UTC wall-clock metadata.
2. Emit **structured log lines** (`obs.log_json_event`) for run boundaries and coarse task events.
3. Capture **per-task output snippets** (redacted, length-capped) via the crew `task_callback`.
4. Capture **instrumented LLM** rows (latency, token deltas, rough USD, retries/failures) from
   `InstrumentedLLM`.
5. Write **`build/run_report_<run_id>.json`** and **`.md`** aggregating meta, tasks, LLM rows,
   optional crew summary, errors, and artifact presence flags (no secrets).

## Non-goals

- Remote log shipping or OpenTelemetry exporters.
- Full prompt/replay of every LLM message body.

## References

- `src/articlebook/shared/observability*.py`, `cli.py`, `cli_execution.py`, `pipeline.py`,
  `gatekeeper_instrumented.py`
- Tests: `tests/test_m9_observability.py`
