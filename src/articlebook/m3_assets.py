"""M3 figure/table/formula assets: whitelisted generators, verification, stub manifest."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from articlebook.inputs import RunInputs

# Paths relative to project root (FR-11).
M3_WHITELISTED_SCRIPTS = (
    "scripts/make_graph.py",
    "scripts/make_image.py",
)
M3_BINARY_ASSETS = ("figures/graph.pdf", "figures/image.png")
# LaTeX sources that reference graphics relative to latex/.
M3_TEX_SNIPPETS = ("latex/chapters/m3_fr9_showcase.tex",)


def run_m3_python_generators(root: Path) -> str:
    """Execute whitelisted Matplotlib scripts; return a short log tail for observability."""
    root = root.resolve()
    lines: list[str] = []
    for rel in M3_WHITELISTED_SCRIPTS:
        script = (root / rel).resolve()
        if not script.is_file() or not str(script).startswith(str(root)):
            lines.append(f"missing_script:{rel}")
            continue
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
        )
        tail = (proc.stderr or proc.stdout or "")[-1500:]
        lines.append(f"{rel} exit={proc.returncode}\n{tail}")
    return "\n---\n".join(lines)


def _collect_includegraphics(tex: str) -> list[str]:
    pat = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
    return pat.findall(tex)


def verify_m3_figure_assets(root: Path) -> tuple[bool, list[str]]:
    """Return (ok, issues) after checking binaries and \\includegraphics targets from latex/."""
    root = root.resolve()
    issues: list[str] = []
    for rel in M3_BINARY_ASSETS:
        p = root / rel
        if not p.is_file():
            issues.append(f"missing:{rel}")
        elif p.stat().st_size == 0:
            issues.append(f"empty:{rel}")

    latex_dir = root / "latex"
    for rel in M3_TEX_SNIPPETS:
        tex_path = root / rel
        if not tex_path.is_file():
            issues.append(f"missing_tex:{rel}")
            continue
        text = tex_path.read_text(encoding="utf-8")
        for raw in _collect_includegraphics(text):
            # Paths in showcase are relative to latex/ (e.g. ../figures/graph.pdf).
            target = (latex_dir / raw).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                issues.append(f"bad_path:{raw}")
                continue
            if not target.is_file():
                issues.append(f"missing_graphics:{raw}")
            elif target.stat().st_size == 0:
                issues.append(f"empty_graphics:{raw}")

    return (len(issues) == 0, issues)


def write_m3_stub_manifest(root: Path, inputs: RunInputs, generator_log: str) -> None:
    """Persist M3 stub run metadata under build/."""
    build = root / "build"
    build.mkdir(parents=True, exist_ok=True)
    ok, issues = verify_m3_figure_assets(root)
    status = "PASS" if ok else "FAIL"
    body = "\n".join(
        [
            "# M3 stub manifest (figures / tables / formulas)",
            "",
            f"- topic: {inputs.topic}",
            f"- language: {inputs.language}",
            f"- asset_check: **{status}**",
            "",
            "## Generated binaries",
            "",
            *[f"- `{p}`" for p in M3_BINARY_ASSETS],
            "",
            "## Generator log (tail)",
            "",
            "```text",
            generator_log.strip()[:8000],
            "```",
            "",
            "## Verification",
            "",
            *(issues if issues else ["- (no issues)"]),
            "",
        ]
    )
    (build / "m3_stub_manifest.md").write_text(body, encoding="utf-8")
