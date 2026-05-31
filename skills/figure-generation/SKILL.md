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
- **Python rule:** only execute **whitelisted** scripts via tools: `scripts/plot_stub_m1.py` (M1),
  `scripts/make_graph.py` and `scripts/make_image.py` (M3) — no arbitrary code strings.
- **M3 contract:** after generation, `verify_m3_assets` checks `figures/graph.pdf`, `figures/image.png`,
  and `\includegraphics` targets referenced from `latex/chapters/m3_fr9_showcase.tex`.
- Every figure/table needs **caption text + label token** even if content is stubbed in M1.
