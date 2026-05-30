---
name: technical-writing
description: Technical writing voice, Markdown chapter structure, and anchor placement for figures/tables/equations in a multi-chapter book.
metadata:
  author: articlebook
  version: "1.0"
---

# Technical writing

- Use **clear hierarchy**: `#` chapter, `##` section, `###` subsection; keep paragraphs tight.
- Define **stable anchors** where assets will land, e.g. `<!-- FIG:pipeline-overview -->`, `<!-- TBL:latency -->`, `<!-- EQ:main-result -->`.
- Maintain **neutral, precise** tone; define acronyms on first use.
- Prefer **Markdown-native** tables only when simple; otherwise leave a labeled placeholder for LaTeX `booktabs` in M4.
