---
name: research-methodology
description: Source vetting heuristics and BibTeX record shape for credible references tied to stable citation keys.
metadata:
  author: articlebook
  version: "1.0"
---

# Research methodology

- Prefer **verifiable** sources (standards bodies, textbooks, peer-reviewed venues). If unavailable, label claims as *hypothesis*.
- **BibTeX keys:** `lastnameYYYYkeyword` lowercased, ASCII only, e.g., `vargas2020crewai`.
- Required **fields** when claiming a paper: `title`, `author`, `year`, `howpublished` or `journal`, and `url` or `doi` when possible.
- In M1, emit **placeholder** `.bib` snippets inside Markdown notes—full `latex/references.bib` lands in M2.
