"""M6 QA report dataclass and serialization."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class M6QAReport:
    """Outcome of :func:`articlebook.m6_qa.run_m6_contract_qa`."""

    passed: bool
    log_prefix_used: str | None
    checks: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_json_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, **asdict(self)}

    def to_markdown(self) -> str:
        lines = [
            "# M6 QA contract report",
            "",
            f"- **passed:** `{self.passed}`",
            f"- **compile_log_prefix:** `{self.log_prefix_used}`",
            "",
            "## Errors",
            "",
        ]
        lines.extend(f"- {e}" for e in self.errors) or lines.append("- _(none)_")
        lines += ["", "## Warnings", ""]
        lines.extend(f"- {w}" for w in self.warnings) or lines.append("- _(none)_")
        lines += ["", "## Check details", "", "```json"]
        lines.append(json.dumps(self.checks, indent=2))
        lines += ["```", ""]
        return "\n".join(lines)
