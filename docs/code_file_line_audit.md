# Code file line audit (≤150 LOC guideline)

Project convention: substantive Python in **`src/articlebook/`** and **`tests/`** should stay **≤ ~150 lines per file** when practical (`SYSTEM_PROMPT.md`, `PROMPTS.md`).

## How this file is maintained

After substantive edits, run from the repository root (Python 3.11+):

```text
py -3 -c "from pathlib import Path
for root in [Path('src/articlebook'), Path('tests')]:
  for p in sorted(root.rglob('*.py')):
    n = sum(1 for _ in p.open(encoding='utf-8'))
    if n > 150:
      print(n, p)"
```

Expect **no output**. If a file appears, split by responsibility (new module + thin re-export) rather than deleting behavior.

## 2026-06-01 split (line-limit pass)

| Former hotspot | Split into |
|----------------|------------|
| `shared/gatekeeper.py` | `gatekeeper_policy.py`, `gatekeeper_instrumented.py`, thin `gatekeeper.py` |
| `m2_stub.py` | `m2_stub_constants.py`, `m2_stub_bib.py`, `m2_stub_outline.py`, `m2_stub_chapter_copy.py`, thin `m2_stub.py` |
| `pipeline_stubs.py` | `pipeline_stub_m1.py`, `pipeline_stub_latex.py`, thin `pipeline_stubs.py` |
| `crew/crew_builder.py` | `crew_milestone_dispatch.py`, thin `crew_builder.py` |
| `crew/workspace_tools.py` | `workspace_m6_reply.py` (M6 tool formatting) |
| `crew/agents.py` | `agent_factory.py`, thin `agents.py` |
| `tests/test_m7_config_and_gatekeeper.py` | `conftest.py` (cache reset), `test_m7_gatekeeper_policy.py`, `test_m7_config_yaml.py` |
