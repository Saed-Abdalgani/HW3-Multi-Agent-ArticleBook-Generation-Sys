"""Stub Matplotlib output for M1 (vector PDF under figures/)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "figures" / "m1_stub_graph.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    xs = list(range(10))
    ys = [x * x for x in xs]
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(xs, ys, label="y=x^2")
    ax.set_title("M1 stub graph")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, format="pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
