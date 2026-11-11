"""Step 3: charts.

Every chart goes through save_figure, so all figures share the same size
settings and are reproducible (acceptance criteria AC-1.3 and AC-2.4).

Chart rules for this project (requirement G-5): a title, labelled axes with
units, a source note, and never colour alone to tell series apart.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to files; no window needed (works in CI too)

import matplotlib.pyplot as plt  # noqa: E402  (must come after the line above)
from matplotlib.figure import Figure  # noqa: E402

from pipelines.paths import FIGURES_DIR  # noqa: E402


def save_figure(figure: Figure, name: str, figures_dir: Path = FIGURES_DIR) -> Path:
    """Save a chart as PNG and return its path.

    The "Software" entry normally stores the matplotlib version inside the
    file. It is removed so the file does not change between versions.
    """
    figures_dir.mkdir(parents=True, exist_ok=True)
    path = figures_dir / f"{name}.png"
    figure.savefig(path, dpi=150, bbox_inches="tight", metadata={"Software": None})
    plt.close(figure)
    return path


# TODO (owner, sprint 1): add the two charts for the trend scan (requirement R-2.5):
#   plot_time_series(counts, trends_config) -> Figure
#   plot_trend_radar(metrics, trends_config) -> Figure
