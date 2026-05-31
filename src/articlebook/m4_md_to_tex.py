"""Markdown subset → LaTeX fragment (M4)."""

from __future__ import annotations

import re


def escape_latex(s: str) -> str:
    """Escape characters that break LaTeX text mode (Unicode preserved)."""
    repl = (
        ("\\", r"\textbackslash{}"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("$", r"\$"),
        ("%", r"\%"),
        ("#", r"\#"),
        ("&", r"\&"),
        ("_", r"\_"),
        ("^", r"\textasciicircum{}"),
        ("~", r"\textasciitilde{}"),
    )
    out = s
    for a, b in repl:
        out = out.replace(a, b)
    return out


def _pandoc_cites_to_parencite(line: str) -> str:
    """Turn [@a; @b] into \\parencite{a,b} (biblatex)."""

    def repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        keys: list[str] = []
        for part in inner.split(";"):
            k = part.strip().lstrip("@").strip()
            if k:
                keys.append(k)
        if not keys:
            return m.group(0)
        return "\\parencite{" + ",".join(keys) + "}"

    return re.sub(r"\[(@[^\]]+)\]", repl, line)


def _texttt(inner: str, *, rtl_heavy: bool) -> str:
    """Inline code span; wrap as an LTR island under RTL layout (FR-13)."""
    code = "\\texttt{" + escape_latex(inner) + "}"
    return "\\textenglish{" + code + "}" if rtl_heavy else code


def _segment_format_plain(seg: str, *, rtl_heavy: bool = False) -> str:
    """Render `` ` `` (code) and **bold** as LaTeX, escaping only plain text runs.

    Plain text is escaped; emitted ``\\texttt``/``\\textbf`` commands are kept intact
    (escaping the whole result would turn commands into literal ``\\textbackslash`` text).
    """
    out: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if buf:
            out.append(escape_latex("".join(buf)))
            buf.clear()

    i = 0
    while i < len(seg):
        if seg[i : i + 2] == "**":
            j = seg.find("**", i + 2)
            if j == -1:
                buf.append(seg[i])
                i += 1
                continue
            flush()
            out.append("\\textbf{" + escape_latex(seg[i + 2 : j]) + "}")
            i = j + 2
            continue
        if seg[i] == "`":
            j = seg.find("`", i + 1)
            if j == -1:
                buf.append(seg[i])
                i += 1
                continue
            flush()
            out.append(_texttt(seg[i + 1 : j], rtl_heavy=rtl_heavy))
            i = j + 1
            continue
        buf.append(seg[i])
        i += 1
    flush()
    return "".join(out)


def _convert_markdown_line(line: str, *, rtl_heavy: bool = False) -> str:
    """Citations, then escape user text around \\parencite segments."""
    line = _pandoc_cites_to_parencite(line)
    parts = re.split(r"(\\parencite\{[^}]+\})", line)
    out: list[str] = []
    for part in parts:
        if part.startswith("\\parencite"):
            out.append(part)
        else:
            out.append(_segment_format_plain(part, rtl_heavy=rtl_heavy))
    return "".join(out)


def _format_body_line(raw: str, *, rtl_heavy: bool) -> str:
    s = raw.rstrip()
    if not s.strip():
        return "\n"
    if s.strip().startswith(">"):
        inner = s.lstrip().lstrip(">").strip()
        inner_tex = _convert_markdown_line(inner, rtl_heavy=rtl_heavy)
        return "\\begin{quote}" + inner_tex + "\\end{quote}\n\n"
    return _convert_markdown_line(s, rtl_heavy=rtl_heavy) + "\n\n"


def markdown_chapter_to_tex(
    md_text: str,
    *,
    chapter_label: str,
    rtl_heavy: bool,
) -> str:
    """Convert minimal Markdown chapter to LaTeX fragment."""
    lines = md_text.strip().splitlines()
    out: list[str] = []
    in_code = False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            out.append("\\begin{verbatim}\n" + line + "\n\\end{verbatim}\n")
            continue
        m1 = re.match(r"^#\s+(.+)$", line)
        if m1:
            title = m1.group(1).strip()
            out.append("\\chapter{" + escape_latex(title) + "}\n")
            out.append("\\label{" + chapter_label + "}\n\n")
            continue
        m2 = re.match(r"^##\s+(.+)$", line)
        if m2:
            out.append("\\section{" + escape_latex(m2.group(1).strip()) + "}\n\n")
            continue
        out.append(_format_body_line(line, rtl_heavy=rtl_heavy))
    return "".join(out).strip() + "\n"


def chapter_label_from_stem(stem: str) -> str:
    return "ch:" + re.sub(r"[^a-zA-Z0-9_:-]", "_", stem)
