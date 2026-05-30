# Mechanism PRD — M1 crew, skills, and workspace tools

## Purpose

Define how milestone **M1** wires CrewAI agents, filesystem-backed **skills**, sandboxed **tools**, and a shared **working directory** so later milestones can swap stub outputs for real research, Markdown, and LaTeX without rewriting orchestration.

## Scope

- In: agent roster, skill packages under `skills/`, `bind_workspace_root` lifecycle, sequential `Crew`, stub vs LLM entrypoints.
- Out: full Markdown book (M2), multi-pass bibliography (M5), QA contract automation beyond placeholders (M6).

## Architecture

1. **House culture** skill is attached at **crew** level; specialists add their own skill directories via `Agent.skills=[...]`.
2. **Gatekeeper** (`articlebook.shared.gatekeeper`) is the only module constructing `LLM` instances from config.
3. **Workspace tools** enforce relative writes under `content/`, `latex/`, `figures/`, `build/`, `scripts/` and allow reads for a small whitelist of repo root docs (`prd.md`, `plan.md`, …).
4. **Programmatic discovery** uses `crewai.skills.discover_skills` via `articlebook.skills_inventory.list_discovered_skills()` for inventories/tests.

## Operational modes

| Mode | When | Behavior |
|------|------|-----------|
| `--stub` | CI / no API key | Deterministic writes + Matplotlib stub + single `lualatex` smoke pass |
| default | `OPENAI_API_KEY` set | Sequential crew executes tasks with tool calls |

## Risks / follow-ups

- ContextVar-bound tools assume tool calls execute in the same context as `bind_workspace_root`; if CrewAI parallelizes tools, migrate to tool classes carrying `root: str`.
- External search tools (SerpAPI, etc.) are intentionally omitted until keys and rate limits live in Gatekeeper.
