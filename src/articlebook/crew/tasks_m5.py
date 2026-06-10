"""CrewAI tasks for milestone M5 (M4 + canonical multipass compile + QA)."""

from __future__ import annotations

from crewai import Agent, Task

from articlebook.crew.tasks_m2 import _WRITE_WS_SINGLE
from articlebook.crew.tasks_m4 import build_m4_tasks


def build_m5_tasks(agents: dict[str, Agent], topic: str, language: str) -> list[Task]:
    """Same as M4 through LaTeX assembly, then **run_latex_canonical_compile** + QA on M5 logs."""
    m4_tasks = build_m4_tasks(agents, topic, language)
    research, outline, writing, figures, latex, _compile_m4, _qa_m4 = m4_tasks
    shared = f"Topic: {topic}\nLanguage: {language}\n"

    compile_ = Task(
        description=shared
        + "After LaTeX assembly (same as M4), run **run_latex_canonical_compile** with "
        "**reason** (first argument, e.g. `m5_run`) and **log_prefix** (second argument) "
        "exactly `m5_crew`. This runs the full engine→biber→engine×N "
        "sequence per plan.md §4. Summarize `ok`, `build/main.pdf`, and the journal JSON path.",
        expected_output=(
            "Canonical multipass compile executed; "
            "journal at build/m5_crew_compile_journal.json."
        ),
        agent=agents["compile"],
        context=[latex],
    )
    qa = Task(
        description=shared
        + "Call **verify_m3_assets**. Read `build/m5_crew_compile_journal.json`; use the log "
        "paths recorded there to read engine pass logs under `build/` for errors. "
        + _WRITE_WS_SINGLE
        + " Save **relative_path** `build/m5_qa_report.md` with **content** covering: compile ok "
        "flag, pdf presence, unresolved citation or reference lines if any, and M3 asset status.",
        expected_output="m5_qa_report.md with M5 compile + contract coverage.",
        agent=agents["qa"],
        context=[compile_],
    )
    return [research, outline, writing, figures, latex, compile_, qa]
