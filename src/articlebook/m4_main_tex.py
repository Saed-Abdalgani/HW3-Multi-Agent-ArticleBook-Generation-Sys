"""Generate ``latex/main.tex`` (preamble, cover, TOC, inputs)."""

from __future__ import annotations

import os
from pathlib import Path

from articlebook.inputs import RunInputs
from articlebook.m4_constants import SHOWCASE_STEM
from articlebook.m4_md_to_tex import escape_latex


def write_main_tex(root: Path, inputs: RunInputs, chapter_stems: list[str]) -> None:
    """Write ``latex/main.tex`` (polyglossia, biblatex+biber, hyperref, cleveref, fancyhdr)."""
    topic_esc = escape_latex(inputs.topic)
    lang_esc = escape_latex(inputs.language)
    author = escape_latex(os.environ.get("ARTICLEBOOK_AUTHOR", "Multi-Agent ArticleBook"))
    pdf_title = inputs.topic.encode("ascii", "replace").decode("ascii").replace("?", " ")

    inputs_block = "\n".join(f"\\input{{chapters/{s}}}" for s in chapter_stems)
    inputs_block += f"\n\\input{{chapters/{SHOWCASE_STEM}}}\n"

    # FR-14: Hebrew runs drive a full RTL document (TOC, headers, captions, numbering);
    # English stays the default LTR layout. polyglossia + LuaLaTeX handle bidi for islands.
    if inputs.text_direction == "rtl":
        default_lang, other_lang = "hebrew", "english"
    else:
        default_lang, other_lang = "english", "hebrew"

    ch_mark = (
        r"\renewcommand{\chaptermark}[1]{\markboth{\chaptername\ \thechapter.\ "
        + "#1"
        + r"}{}}"
    )

    hyp = (
        "\\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,citecolor=blue,pdftitle={"
        + pdf_title
        + "},pdfauthor={"
        + author
        + "}}"
    )

    lines: list[str] = [
        r"\documentclass[12pt,a4paper,twoside,openany]{book}",
        r"% --- M4: preamble ---",
        r"\usepackage{fontspec}",
        r"\usepackage{polyglossia}",
        rf"\setdefaultlanguage{{{default_lang}}}",
        rf"\setotherlanguage{{{other_lang}}}",
        r"\newfontfamily\hebrewfont[Script=Hebrew,Scale=MatchUppercase]{Arial}",
        r"\usepackage{graphicx}",
        r"\usepackage{tikz}",
        r"\usetikzlibrary{arrows.meta,positioning}",
        r"\usepackage{booktabs}",
        r"\usepackage{amsmath}",
        r"\usepackage{amssymb}",
        r"\usepackage{mathtools}",
        r"\usepackage{csquotes}",
        r"\usepackage[backend=biber,style=numeric-comp,sorting=nyt]{biblatex}",
        r"\addbibresource{references.bib}",
        r"\usepackage{hyperref}",
        hyp,
        r"\usepackage[nameinlink,capitalize]{cleveref}",
        r"\usepackage{fancyhdr}",
        r"\pagestyle{fancy}",
        r"\fancyhf{}",
        r"\fancyhead[LE,RO]{\thepage}",
        r"\fancyhead[LO]{\nouppercase{\rightmark}}",
        r"\fancyhead[RE]{\nouppercase{\leftmark}}",
        ch_mark,
        rf"\title{{{topic_esc}}}",
        rf"\author{{{author}}}",
        r"\date{\today}",
        r"\begin{document}",
        r"\frontmatter",
        r"\begin{titlepage}",
        r"\centering",
        r"\vspace*{2cm}",
        rf"{{\Huge\bfseries {topic_esc}\par}}",
        r"\vspace{1.2cm}",
        r"{\LARGE Thematic cover (M4)\par}",
        r"\vspace{0.6cm}",
        rf"{{\large\itshape {lang_esc}\par}}",
        r"\vfill",
        rf"{{\Large {author}\par}}",
        r"\vspace{0.5cm}",
        r"{\large \today\par}",
        r"\end{titlepage}",
        r"% M6: keep TOC compact — Markdown ## becomes \section; listing them can add many pages.",
        r"\setcounter{tocdepth}{0}",
        r"\tableofcontents",
        r"\listoffigures",
        r"\listoftables",
        r"\mainmatter",
        inputs_block.rstrip(),
        r"\backmatter",
        r"\printbibliography[title={References}]",
        r"\end{document}",
        "",
    ]
    (root / "latex" / "main.tex").write_text("\n".join(lines), encoding="utf-8")
