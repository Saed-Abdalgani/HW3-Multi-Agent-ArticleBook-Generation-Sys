"""CrewAI tasks for milestone M6 (M5 + deterministic contract QA tool)."""

from __future__ import annotations

from crewai import Agent, Task

from articlebook.crew.tasks_m5 import build_m5_tasks


def build_m6_tasks(agents: dict[str, Agent], topic: str, language: str) -> list[Task]:
    """M5 pipeline with M6 compile journal prefix and **run_m6_contract_checks** for QA."""
    m5 = build_m5_tasks(agents, topic, language)
    research, outline, writing, figures, latex, _compile_m5, _qa_m5 = m5
    shared = f"Topic: {topic}\nLanguage: {language}\n"

    compile_ = Task(
        description=shared
        + "After LaTeX assembly, run **run_latex_canonical_compile** with log_prefix `m6_crew` "
        "(second argument). Full engine→biber→engine×N sequence per plan.md §4.",
        expected_output=(
            "Journal at build/m6_crew_compile_journal.json; "
            "build/main.pdf if engine ok."
        ),
        agent=agents["compile"],
        context=[latex],
    )
    qa = Task(
        description=shared
        + "Call **run_m6_contract_checks** with log_prefix `m6_crew` (second argument). "
        "Summarize pass/fail; note `build/m6_qa_report.md`. "
        "Visual BiDi check (FR-13) remains manual.",
        expected_output="M6 contract QA executed via run_m6_contract_checks.",
        agent=agents["qa"],
        context=[compile_],
    )
    return [research, outline, writing, figures, latex, compile_, qa]
