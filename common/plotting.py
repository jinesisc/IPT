
"""
Shared plot style so figures from every problem look consistent.

Usage:
    from common.plotting import apply_style, COLORS, INK2, save_figure
    apply_style()
    fig, ax = plt.subplots()
    ax.plot(x, y, color=COLORS[0])
    save_figure(fig, out_dir, "my_plot.png")

Use COLORS in order (series 1 = COLORS[0], series 2 = COLORS[1], ...) so a given
series keeps the same color across figures.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

# Categorical palette (fixed order; colorblind-checked for adjacent pairs)
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK = "#0b0b0b"     # titles
INK2 = "#52514e"    # labels, annotations, reference lines
GRID = "#e4e3df"
SURFACE = "#fcfcfb"


def apply_style(interactive: bool = False) -> None:
    """Apply the shared style. interactive=False uses a non-GUI backend (just saves files)."""
    if not interactive:
        matplotlib.use("Agg")
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.labelsize": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "xtick.color": INK2, "ytick.color": INK2, "lines.linewidth": 2,
        "legend.frameon": False, "legend.fontsize": 9, "font.size": 10,
        "savefig.dpi": 150, "savefig.bbox": "tight",
    })


def save_figure(fig, out_dir: str | Path, name: str) -> Path:
    """Save a figure into out_dir (created if needed), close it, and return its path."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    fig.savefig(path)
    plt.close(fig)
    return path
