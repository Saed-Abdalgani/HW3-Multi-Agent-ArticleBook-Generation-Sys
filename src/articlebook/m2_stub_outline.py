"""Outline Markdown for M2 stub."""

from articlebook.m2_stub_constants import PAGE_TARGET_HI, PAGE_TARGET_LO, WORDS_PER_PAGE


def outline_md(topic: str, language: str, direction: str) -> str:
    rows = [
        "| # | Chapter file | Title | Pages | Words | Notes |",
        "|---|--------------|-------|-------|-------|-------|",
        (
            "| 1 | `chapter_01_scope.md` | Scope, audience, definitions | 5 | 1300 | "
            "Cites [@knuth1984texbook]. |"
        ),
        (
            "| 2 | `chapter_02_markdown_first.md` | Markdown-first authoring | 5 | 1300 | "
            "[@markdownguide2024]. |"
        ),
        (
            "| 3 | `chapter_03_agents_and_crews.md` | Agents, crews, task graphs | 6 | 1700 | "
            "[@crewai2024docs; @short2024llm]. |"
        ),
        (
            "| 4 | `chapter_04_bidi_technical_note.md` | **BiDi demo** (RTL/LTR) | 4 | 1200 | "
            "**Reserved** FR-13; Hebrew + English islands. |"
        ),
        (
            "| 5 | `chapter_05_latex_path.md` | Markdown to LaTeX | 3 | 750 | "
            "[@lamport1994latex]. |"
        ),
        (
            "| 6 | `chapter_06_conclusion.md` | Conclusion, risks, next steps | 3 | 750 | "
            "Wrap-up; no new citations. |"
        ),
    ]
    total_pages = 5 + 5 + 6 + 4 + 3 + 3
    total_words = 0
    for r in rows[2:]:
        parts = [p.strip() for p in r.split("|")]
        if len(parts) > 6 and parts[1].isdigit() and parts[5].isdigit():
            total_words += int(parts[5])
    return "\n".join(
        [
            f"# Outline: {topic}",
            "",
            f"- **Primary language:** {language}",
            f"- **Base text direction:** {direction}",
            f"- **Page target:** {PAGE_TARGET_LO}–{PAGE_TARGET_HI} "
            f"(this outline: **~{total_pages} pages**).",
            (
                f"- **Aggregate word budget:** ~{total_words} words "
                f"(~{total_pages * WORDS_PER_PAGE} at {WORDS_PER_PAGE} w/page)."
            ),
            "",
            "## Chapter plan",
            "",
            *rows,
            "",
            "## Asset anchors (stable labels for M3/M4)",
            "",
            "- `<!-- ASSET:FIG fig:pipeline diagram.pdf -->` — system diagram (M3).",
            "- `<!-- ASSET:IMG fig:cover-art image.png -->` — thematic image (M3).",
            "- `<!-- ASSET:GRAPH fig:latency graph.pdf -->` — Python/Matplotlib graph (M3).",
            "- `<!-- ASSET:TAB tab:requirements -->` — requirements table (M3).",
            "- `<!-- ASSET:EQ eq:normalized -->` — displayed equation with `\\label` (M3/M4).",
            "",
        ]
    )
