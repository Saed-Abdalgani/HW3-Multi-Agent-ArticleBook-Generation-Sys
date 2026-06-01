# PRD — M7 Production Harness (Gatekeeper & Config)

| Field | Value |
|-------|-------|
| Parent | `plan.md` §10.1, §10.2, §10.5, §11 (Phase 7 / Milestone M7) |
| Status | Implemented |

## Purpose

Move implicit “harness” behavior into explicit, testable modules:

- **Gatekeeper** wraps CrewAI `LLM` calls with retries, optional soft rate limiting, latency + token-delta logging, and rough cost estimates (non-authoritative).
- **Configuration** externalizes model/gatekeeper/RAG flags to `config/models.yaml` with environment-variable overrides for secrets and operational hotfixes.
- **Agents & tasks** can be tuned without code edits via `config/agents.yaml` and `config/tasks.yaml` overlays (tools remain code-defined).

## Functional requirements

1. **FR-GK-1** LLM construction preserves the public `create_llm(config)` entry point.
2. **FR-GK-2** Retries use exponential backoff with jitter on transient provider/network failures.
3. **FR-GK-3** `timeout` flows from merged config into CrewAI `LLM(timeout=…)` when present.
4. **FR-CFG-1** Missing YAML files fall back to Python defaults (backward compatible).
5. **FR-CFG-2** Resolved non-secret run metadata is written to `build/resolved_run_config.json` on each LLM pipeline start.

## Non-goals (M7)

- Human approval gates, red-team security suite (**M8**).
- Structured per-stage run reports (**M9**).
- Changing `--stub` semantics or CLI flags.

## Acceptance

- `uv run pytest tests/` passes including new M7 unit tests.
- `uv run ruff check src tests` is clean for touched paths.
- `skills/compilation/SKILL.md` ships and is attached to the Compilation agent.
