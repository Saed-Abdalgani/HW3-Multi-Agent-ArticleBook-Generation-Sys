"""Deterministic Matplotlib export for M3 (FR-9 Python-generated graph -> figures/graph.pdf)."""

from __future__ import annotations

import math
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "figures" / "graph.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)

    rng = random.Random(42)
    xs = list(range(24))
    ys = [0.5 * math.sin(x / 3.0) + 0.25 * rng.random() for x in xs]

    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    ax.plot(xs, ys, color="#1f77b4", linewidth=2.0, marker="o", markersize=3, label="synthetic series")
    ax.fill_between(xs, ys, alpha=0.15, color="#1f77b4")
    ax.set_title("Deterministic pipeline latency model (stub data)")
    ax.set_xlabel("Stage index")
    ax.set_ylabel("Relative load")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(loc="upper right", frameon=True)
    fig.tight_layout()
    fig.savefig(out, format="pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
