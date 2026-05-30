---
name: qa-checklist
description: Technical contract checklist for links, citations, BiDi, required FR-9 elements, and compilation diagnostics before declaring a build READY.
metadata:
  author: articlebook
  version: "1.0"
---

# QA checklist (M1 = placeholders)

1. **Artifacts exist** on disk for each stage (research, outline, writing, figures, TeX stub, compile log, QA report).
2. **Compilation log** captured under `build/`; classify `! LaTeX Error` vs warnings.
3. **Figures path probe:** every declared `\includegraphics` target must resolve in later milestones.
4. **Secrets:** confirm no API keys in logs or `build/*.log`.
5. **Stub honesty:** if PDF not produced yet, state that explicitly in the QA report.
