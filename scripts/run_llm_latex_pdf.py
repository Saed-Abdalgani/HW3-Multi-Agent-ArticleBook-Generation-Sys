"""LLM crew → Markdown → LaTeX → PDF (delegates to ``articlebook`` CLI).

Prepends the repo ``src/`` directory to ``sys.path`` so you can run this file
with ``uv run python scripts/run_llm_latex_pdf.py ...`` even when you rely on a
plain checkout instead of an editable install.

Equivalent CLI (after ``uv sync``)::

    uv run articlebook --topic \"...\" --language English --milestone m6

Use ``--milestone m4`` for crew-driven LaTeX + compile; ``m5`` or ``m6`` for the
canonical multipass engine + biber loop (``m6`` adds deterministic contract QA).
For a real PDF, MiKTeX (``lualatex``, ``biber``) should be on ``PATH``; for CI
or machines without LaTeX, pass ``--m6-allow-missing-pdf`` when using ``m6``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from articlebook.cli import main  # noqa: E402, I001


if __name__ == "__main__":
    main()
