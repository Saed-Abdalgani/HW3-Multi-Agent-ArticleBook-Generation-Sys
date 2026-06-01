"""Curated BibTeX corpus for deterministic M2 stub chapters."""


def bibtex_corpus() -> str:
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
