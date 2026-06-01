# PRD — M8 security & human-in-the-loop

This document pins **Milestone M8** behavior from `plan.md` §11 and `todo.md` Phase M8.

## Objectives

1. Reject obviously abusive **topic** input (control characters + prompt-injection heuristics).
2. Treat **workspace file reads** as untrusted: size limits, injection-density collapse, and a
   visible notice appended to tool output.
3. Block **tool writes** that match a small denylist (path escape / shell tropes).
4. Enforce **overwrite policy** on `write_workspace_file` for non-`build/` paths when a file
   already exists, unless the operator has acknowledged (`--yes` / interactive flow) or the
   paid crew session explicitly enables overwrites inside `run_llm`.
5. Support **`--dry-run`** (no stub disk writes; crew writes are no-ops) and **`--yes`**
   (skip interactive confirmations).
6. Require **human confirmation** before the paid LLM path when stdin/stdout are TTYs.

## Non-goals

- Full content safety moderation of generated prose.
- Network egress controls beyond existing gatekeeper settings.

## References

- Implementation: `src/articlebook/shared/security*.py`, `cli_preflight.py`,
  `crew/workspace_io_security.py`, `skills/security-review/SKILL.md`.
- Tests: `tests/test_m8_security_redteam.py`.
