"""CrewAI tasks for milestone M4 (LaTeX assembly + compile + QA)."""

from __future__ import annotations

from crewai import Agent, Task

from articlebook.crew.tasks_m2 import _WRITE_WS_SINGLE
from articlebook.crew.tasks_m3 import build_m3_tasks


def build_m4_tasks(agents: dict[str, Agent], topic: str, language: str) -> list[Task]:
    """M3 content + figures, then LaTeX assembly + one compile + QA (M4)."""
    m3_tasks = build_m3_tasks(agents, topic, language)
    research, outline, writing, figures, _qa_m3 = m3_tasks
    shared = f"Topic: {topic}\nLanguage: {language}\n"

    latex = Task(
        description=shared
        + "Call **assemble_latex_document** with the exact same topic and language strings "
        f"as in this task header: topic={topic!r}, language={language!r}. "
        "This regenerates `latex/main.tex` and the per-chapter `.tex` files under "
        "`latex/chapters/` produced from each Markdown chapter. "
        "Then read the first 80 lines of `latex/main.tex` via read_workspace_file to confirm "
        "biblatex, hyperref, cleveref, fancyhdr, and polyglossia are present.",
        expected_output="assemble_latex_document succeeded; main.tex contains M4 preamble markers.",
        agent=agents["latex"],
        context=[figures],
    )
    compile_ = Task(
        description=shared
        + "Run **run_lualatex_once** with **reason** (first argument, e.g. `m4_compile`) and "
        "**log_filename** (second argument) exactly `m4_lualatex_once.log`. "
        "Summarize the exit code and whether `build/main.pdf` "
        "exists (M4 allows undefined citations until M5 biber passes).",
        expected_output="One LuaLaTeX pass executed; log at build/m4_lualatex_once.log.",
        agent=agents["compile"],
        context=[latex],
    )
    qa = Task(
        description=shared
        + "Call **verify_m3_assets** and record the result. Read `build/m4_lualatex_once.log` "
        "for fatal errors. Confirm `latex/chapters/chapter_01_scope.tex` exists and references "
        "`\\parencite` where Markdown had citations. "
        + _WRITE_WS_SINGLE
        + " Save **relative_path** `build/m4_qa_report.md` with **content** as tables "
        "for M3 asset checks, assembly checks, and compile checks (check, status, evidence).",
        expected_output="m4_qa_report.md saved with M4 contract coverage.",
        agent=agents["qa"],
        context=[compile_],
    )
    return [research, outline, writing, figures, latex, compile_, qa]
