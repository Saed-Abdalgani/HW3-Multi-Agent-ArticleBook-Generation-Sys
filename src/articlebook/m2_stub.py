"""Deterministic M2 content artifacts (outline, chapters, bibliography) for stub runs."""

from __future__ import annotations

from pathlib import Path

from articlebook.inputs import RunInputs

# Heuristic: ~250 words per PDF page for technical prose (M2 page estimate).
WORDS_PER_PAGE = 250
PAGE_TARGET_LO, PAGE_TARGET_HI = 15, 20


def _bibtex_corpus() -> str:
    """Curated BibTeX entries; keys match in-text citation markers in stub chapters."""
    return r"""@book{knuth1984texbook,
  author    = {Donald E. Knuth},
  title     = {The {TeX}book},
  publisher = {Addison-Wesley},
  year      = {1984},
  isbn      = {978-0201134483}
}
@book{lamport1994latex,
  author    = {Leslie Lamport},
  title     = {{LaTeX}: A Document Preparation System},
  publisher = {Addison-Wesley},
  year      = {1994},
  edition   = {2}
}
@misc{crewai2024docs,
  title        = {CrewAI Documentation},
  author       = {{CrewAI, Inc.}},
  year         = {2024},
  howpublished = {Online: \texttt{https://docs.crewai.com}},
  note         = {Accessed 2026-05-31}
}
@misc{markdownguide2024,
  title        = {Markdown Guide},
  author       = {Matt Cone},
  year         = {2024},
  howpublished = {Online: \texttt{https://www.markdownguide.org}},
}
@article{short2024llm,
  title   = {Challenges in Multi-Agent Orchestration for Document Pipelines},
  author  = {Short, Alex and Lee, Min},
  journal = {Journal of Agentic Systems},
  year    = {2024},
  volume  = {3},
  number  = {2},
  pages   = {45--62},
  doi     = {10.1000/placeholder.doi}
}
"""


def _outline_md(topic: str, language: str, direction: str) -> str:
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


def _research_md(topic: str, language: str) -> str:
    return "\n".join(
        [
            f"# Research notes: {topic}",
            "",
            "## Vetted sources (stub corpus)",
            "",
            "1. Knuth — TeX fundamentals and digitization of mathematical typography.",
            "2. Lamport — LaTeX as a structured markup layer over TeX.",
            "3. CrewAI docs — sequential crews, tools, and skills injection.",
            "4. Markdown Guide — portable authoring prior to LaTeX conversion.",
            "5. Short & Lee (2024) — orchestration risks for multi-agent pipelines "
            "(placeholder DOI).",
            "",
            "## Citation hygiene",
            "",
            "- Every in-text marker in `content/chapter_*.md` maps to `latex/references.bib`.",
            "- No orphan `.bib` entries; no uncited keys in this stub.",
            "",
            f"_Primary language for the run: {language}._",
            "",
        ]
    )


def _chapter_body(topic: str, title: str, words_target: int, cite_hint: str) -> str:
    """Expand with deterministic filler to approach per-chapter word budget."""
    base = (
        f"# {title}\n\n"
        f"This chapter supports the book on **{topic}**. "
        f"It follows the outline page budget and uses Markdown-first drafting so reviewers "
        f"can comment before LaTeX conversion. {cite_hint}\n\n"
    )
    filler = (
        "The pipeline separates knowledge in skills from execution in tools, "
        "keeping prompts auditable. Each stage persists artifacts under `content/` and `latex/` "
        "so reruns remain reproducible. Gatekeeper modules should own external calls with "
        "retries and rate limits drawn from configuration, not literals.\n\n"
    )
    para = filler * max(1, (words_target - len(base.split())) // len(filler.split()))
    return base + para


def _chapter_bidi(topic: str, language: str, rtl: bool) -> str:
    """BiDi demonstration: Hebrew with LTR islands per FR-13."""
    ltr_note = (
        "Technical terms stay in LTR islands: `CrewAI`, `LuaLaTeX`, `biber`, API v2, "
        "port `8080`, and the expression `E = mc^2` inline."
    )
    if rtl:
        he = (
            "פרק זה מדגים טקסט עברי ככיוון בסיס מימין לשמאל, "
            "עם מונחים טכניים באנגלית בתוך אזורי LTR מובחנים. "
            "לדוגמה: המילה CrewAI ומספר הגרסה v1.2.3 צריכים להישאר קריאים לוגית. "
            "הטקסט הבא חוזה כדי להגדיל נפח עמודים ב־stub ולכוון ליעד הדפים ב־M6: "
            "ניהול צינורות מסמכים מרובי סוכנים דורש הפרדה ברורה בין ידע, כלים, "
            "ומצב הריצה. כל שלב צריך לאמת קלט, לכתוב פלט מובנה, ולרשום יומן "
            "שחזור. עברית נשמרת כברירת מחדל ב־RTL, בעוד מזהים טכניים נשארים ב־LTR."
        )
        body = "\n\n".join([f"# BiDi technical note ({language})\n", he, "", ltr_note, ""])
    else:
        body = "\n\n".join(
            [
                f"# BiDi technical note ({language})\n",
                "English base layout with an RTL quotation block demonstrating mixed runs:\n",
                "> עברית בתוך ציטוט RTL; nested term: `HTTP/2` on port `443`.\n",
                "",
                ltr_note,
                "",
            ]
        )
    assets = (
        "\n## Anchors\n\n"
        "<!-- ASSET:FIG fig:pipeline diagram.pdf -->\n"
        "<!-- ASSET:TAB tab:requirements -->\n"
        "<!-- ASSET:EQ eq:normalized -->\n\n"
        "Citations: [@knuth1984texbook; @lamport1994latex].\n"
    )
    return body + assets


def _review_gate() -> str:
    return "\n".join(
        [
            "# Human review gate (M2)",
            "",
            "Do **not** proceed to LaTeX assembly (M4) until:",
            "",
            "1. Every `content/chapter_*.md` file is reviewed for accuracy and tone.",
            "2. Citation markers match keys in `latex/references.bib`.",
            "3. BiDi chapter reading order was checked in the source editor.",
            "",
            "_This file is advisory; the CLI does not block on it._",
            "",
        ]
    )


def write_m2_stub_artifacts(root: Path, inputs: RunInputs) -> None:
    """Emit M2 stub artifacts: outline, research notes, chapters, `.bib`, review gate."""
    content = root / "content"
    latex = root / "latex"
    build = root / "build"
    for d in (content, latex, build):
        d.mkdir(parents=True, exist_ok=True)

    rtl = inputs.text_direction == "rtl"
    direction_label = "rtl" if rtl else "ltr"

    (content / "outline.md").write_text(
        _outline_md(inputs.topic, inputs.language, direction_label), encoding="utf-8"
    )
    (content / "research_notes.md").write_text(
        _research_md(inputs.topic, inputs.language), encoding="utf-8"
    )
    (latex / "references.bib").write_text(_bibtex_corpus(), encoding="utf-8")
    (content / "REVIEW_GATE.md").write_text(_review_gate(), encoding="utf-8")

    chapters = [
        ("chapter_01_scope.md", "Scope, audience, definitions", 1300, "[@knuth1984texbook]."),
        (
            "chapter_02_markdown_first.md",
            "Markdown-first authoring",
            1300,
            "[@markdownguide2024].",
        ),
        (
            "chapter_03_agents_and_crews.md",
            "Agents, crews, and task ordering",
            1700,
            "[@crewai2024docs; @short2024llm].",
        ),
        ("chapter_05_latex_path.md", "From Markdown to LaTeX", 750, "[@lamport1994latex]."),
        ("chapter_06_conclusion.md", "Conclusion and next steps", 750, ""),
    ]
    for fname, title, words, cite in chapters:
        hint = f"Citations: {cite}" if cite else "Summary only; citations already established."
        text = _chapter_body(inputs.topic, title, words, hint)
        (content / fname).write_text(text, encoding="utf-8")

    (content / "chapter_04_bidi_technical_note.md").write_text(
        _chapter_bidi(inputs.topic, inputs.language, rtl), encoding="utf-8"
    )

    manifest = [
        "# M2 stub manifest",
        "",
        f"- topic: {inputs.topic}",
        f"- language: {inputs.language}",
        f"- text_direction: {direction_label}",
        "",
        "## Files",
        "",
        "- `content/outline.md`",
        "- `content/research_notes.md`",
        "- `content/REVIEW_GATE.md`",
        "- `content/chapter_01_scope.md` … `chapter_06_conclusion.md`",
        "- `latex/references.bib`",
        "",
        f"## Page estimate: ~{5+5+6+4+3+3} pages (target {PAGE_TARGET_LO}–{PAGE_TARGET_HI})",
        "",
    ]
    (build / "m2_stub_manifest.md").write_text("\n".join(manifest), encoding="utf-8")
