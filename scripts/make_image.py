"""Raster image asset for M3 (FR-9 thematic PNG -> figures/image.png, Matplotlib-only)."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def _field(n: int = 400) -> list[list[float]]:
    """Deterministic 2D scalar field (no NumPy dependency)."""
    z: list[list[float]] = []
    scale = 2.0 / max(n - 1, 1)
    for i in range(n):
        row: list[float] = []
        yi = -1.0 + i * scale
        for j in range(n):
            xj = -1.0 + j * scale
            row.append(
                math.sin(xj * yi * 8.0) * math.exp(-0.9 * (xj * xj + yi * yi))
                + 0.12 * math.sin(18.0 * xj)
            )
        z.append(row)
    return z


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "figures" / "image.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    z = _field(400)
    fig, ax = plt.subplots(figsize=(4.0, 4.0), dpi=150)
    ax.imshow(z, cmap="magma", origin="lower", interpolation="bilinear")
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    fig.savefig(out, format="png", dpi=200, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


if __name__ == "__main__":
    main()
