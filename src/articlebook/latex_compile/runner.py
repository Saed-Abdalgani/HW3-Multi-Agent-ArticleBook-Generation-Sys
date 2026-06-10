"""Mutable per-build state for engine/biber subprocess steps."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from articlebook.latex_compile.cmd import run_cmd_capture_log
from articlebook.latex_compile.env import biber_available
from articlebook.latex_compile.types import CompilePassRecord, CompileReport, LaTeXEngine


def copy_bib_files_latex_to_build(latex_dir: Path, build_dir: Path) -> None:
    """Mirror ``latex/*.bib`` into ``build/`` so ``biber`` (cwd build) resolves ``\\addbibresource`` paths."""
    build_dir.mkdir(parents=True, exist_ok=True)
    for bib in sorted(latex_dir.glob("*.bib")):
        shutil.copy2(bib, build_dir / bib.name)


@dataclass
class PassRunner:
    root: Path
    latex_dir: Path
    build_dir: Path
    log_prefix: str
    chosen: LaTeXEngine
    report: CompileReport
    step: int = 0

    def engine_cmd(self) -> list[str]:
        return [
            self.chosen,
            "-interaction=nonstopmode",
            f"-output-directory={self.build_dir.resolve()}",
            "main.tex",
        ]

    def run_engine(self, tag: str) -> subprocess.CompletedProcess[str]:
        self.step += 1
        cmd = self.engine_cmd()
        log_path = self.build_dir / f"{self.log_prefix}_pass{self.step:02d}_{tag}_{self.chosen}.log"
        proc = run_cmd_capture_log(cmd, cwd=self.latex_dir, log_path=log_path)
        rel = log_path.relative_to(self.root).as_posix()
        self.report.passes.append(
            CompilePassRecord(
                name=f"{tag}:{self.chosen}",
                command=cmd,
                cwd=str(self.latex_dir.resolve()),
                returncode=proc.returncode,
                log_relative=rel,
            )
        )
        return proc

    def run_biber(self) -> subprocess.CompletedProcess[str]:
        self.step += 1
        cmd = ["biber", "main"]
        log_path = self.build_dir / f"{self.log_prefix}_pass{self.step:02d}_biber.log"
        if not biber_available():
            msg = "biber not on PATH; biblatex resolution may fail.\n"
            log_path.write_text(msg, encoding="utf-8")
            self.report.passes.append(
                CompilePassRecord(
                    name="biber:skipped",
                    command=cmd,
                    cwd=str(self.build_dir.resolve()),
                    returncode=1,
                    log_relative=log_path.relative_to(self.root).as_posix(),
                )
            )
            return subprocess.CompletedProcess(cmd, 1, "", msg)

        # LuaLaTeX writes the .bcf into build/; biber resolves relative bib paths from there.
        copy_bib_files_latex_to_build(self.latex_dir, self.build_dir)

        proc = run_cmd_capture_log(cmd, cwd=self.build_dir, log_path=log_path)
        self.report.passes.append(
            CompilePassRecord(
                name="biber",
                command=cmd,
                cwd=str(self.build_dir.resolve()),
                returncode=proc.returncode,
                log_relative=log_path.relative_to(self.root).as_posix(),
            )
        )
        return proc
