"""Research notes, chapter filler, BiDi demo, and review gate Markdown for M2 stub."""


def research_md(topic: str, language: str) -> str:
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


def chapter_body(topic: str, title: str, words_target: int, cite_hint: str) -> str:
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


def chapter_bidi(topic: str, language: str, rtl: bool) -> str:
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


def review_gate() -> str:
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
