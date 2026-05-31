"""Log heuristics and failure classification for LaTeX/biber runs."""


def needs_extra_engine_pass(log_text: str) -> bool:
    """Heuristic: LaTeX wants another pass (TOC, cites, page refs)."""
    needles = (
        "Rerun to get",
        "rerunfilecheck Warning: File",
        "LaTeX Warning: Label(s) may have changed",
        "There were undefined references",
        "There were undefined citations",
        "Package biblatex Warning: Please (re)run Biber",
        "Package biblatex Warning: Please rerun LaTeX",
    )
    return any(n in log_text for n in needles)


def collect_unresolved_markers(log_text: str) -> list[str]:
    """Pull lines suggesting broken cites/refs (for diagnostics)."""
    out: list[str] = []
    for line in log_text.splitlines():
        if "undefined" in line.lower() or ("Citation" in line and "undefined" in line):
            out.append(line.strip())
    return out[:40]


def classify_compile_failure(stderr: str, stdout: str) -> str:
    blob = (stderr + "\n" + stdout).lower()
    if "undefined control sequence" in blob:
        return "undefined_control_sequence"
    if "! LaTeX Error:" in stderr or "! LaTeX Error:" in stdout:
        return "latex_error"
    if "not found" in blob and "font" in blob:
        return "missing_font"
    if "file not found" in blob or "cannot find" in blob:
        return "missing_file"
    if "missing $." in blob or "missing $" in blob:
        return "math_syntax"
    if "biber" in blob and ("error" in blob or "failed" in blob):
        return "biber_error"
    return "unknown"
