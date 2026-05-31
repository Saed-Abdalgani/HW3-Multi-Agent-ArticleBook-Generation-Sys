"""Milestone M6 — deterministic QA contract (FR-20, prd.md §9).

Implementation is split across ``m6_qa_parse``, ``m6_qa_surface``, ``m6_qa_report``,
``m6_qa_build_phase``, and ``m6_qa_runner`` (each module under ~150 LOC).
"""

from __future__ import annotations

from articlebook.m6_qa_parse import extract_cite_keys_from_tex, parse_bib_keys
from articlebook.m6_qa_report import M6QAReport
from articlebook.m6_qa_runner import run_m6_contract_qa

__all__ = [
    "M6QAReport",
    "extract_cite_keys_from_tex",
    "parse_bib_keys",
    "run_m6_contract_qa",
]
