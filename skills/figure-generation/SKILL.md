---
name: figure-generation
description: Conventions for diagrams, Matplotlib graphs, raster images, tables, and vector-first exports with stable `figures/` paths.
metadata:
  author: articlebook
  version: "1.0"
---

# Figure generation

- **Vector first:** prefer **PDF** for plots/diagrams; PNG only when raster is required.
- **Paths:** reference assets as `../figures/<name>.pdf` from `latex/` includes (builder will normalize in M4).
- **Python rule:** only execute **whitelisted** scripts (e.g., `scripts/plot_stub_m1.py`) via the provided tool—no arbitrary code strings.
- Every figure/table needs **caption text + label token** even if content is stubbed in M1.
