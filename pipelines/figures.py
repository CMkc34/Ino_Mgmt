"""Step 3: charts.

Every chart goes through save_figure, so all figures share the same size
settings and are reproducible (acceptance criteria AC-1.3 and AC-2.4).

Chart rules for this project (requirement G-5): a title, labelled axes with
units, a source note, and never colour alone to tell series apart.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to files; no window needed (works in CI too)

# Ignore any chart settings stored on this particular computer and use the
# font that ships with matplotlib. Otherwise the same code would draw
# different files on different machines.
matplotlib.rcdefaults()
matplotlib.rcParams["font.family"] = "DejaVu Sans"

import matplotlib.pyplot as plt  # noqa: E402  (must come after the line above)
import matplotlib.ticker as ticker  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.transforms import Bbox  # noqa: E402

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


INK = "#1a1a1a"    # lines, markers and text
MUTED = "#6b6b6b"  # helper lines and notes


def short_label(label: str) -> str:
    """The label without an explanation in brackets, for tight spaces."""
    return label.split(" (")[0]


def labels_by_id(trends_config: dict) -> dict[str, str]:
    return {subtopic["id"]: short_label(subtopic["label"]) for subtopic in trends_config["subtopics"]}


def source_note(trends_config: dict, fetch_date: str) -> str:
    return f"Source: {trends_config['source']}, publication counts fetched {fetch_date}. Own calculation."


def plot_time_series(counts: pd.DataFrame, results: pd.DataFrame, trends_config: dict, fetch_date: str) -> Figure:
    """Small panels, one per sub-topic: works per year (method note, section 6.1).

    Panels follow the order of the result table (strongest relative momentum
    first, emerging sub-topics last). Every panel has its own vertical axis
    starting at zero, because the sub-topics differ too much in size.
    """
    labels = labels_by_id(trends_config)
    last_year = trends_config["last_year"]
    order = list(results["subtopic_id"])
    emerging = dict(zip(results["subtopic_id"], results["emerging"]))

    columns = 5
    rows = -(-len(order) // columns)  # round up
    figure, grid = plt.subplots(rows, columns, figsize=(3.1 * columns, 2.6 * rows), sharex=True)
    panels = list(grid.flat)

    for panel, subtopic_id in zip(panels, order):
        series = counts[counts["subtopic_id"] == subtopic_id].sort_values("year")
        earlier = series[series["year"] < last_year]
        latest = series[series["year"] == last_year]
        panel.plot(series["year"], series["works_count"], color=INK, linewidth=1.3)
        panel.plot(earlier["year"], earlier["works_count"], "o", color=INK, markersize=3.5)
        # The latest year is drawn hollow: it is the least settled figure.
        panel.plot(latest["year"], latest["works_count"], "o", color=INK, markerfacecolor="white", markersize=6)
        panel.set_title(labels[subtopic_id], fontsize=9, loc="left")
        if emerging[subtopic_id]:
            panel.text(0.04, 0.93, "emerging", transform=panel.transAxes, fontsize=8.5, color=MUTED, style="italic", va="top")
        panel.set_ylim(bottom=0)
        panel.set_xticks([year for year in series["year"] if year % 5 == 0])
        panel.tick_params(labelsize=8)
        panel.spines[["top", "right"]].set_visible(False)

    for panel in panels[len(order):]:
        panel.set_visible(False)

    figure.suptitle(
        "AI in industrial manufacturing: works per year by sub-topic",
        x=0.01, ha="left", fontsize=13, fontweight="bold",
    )
    figure.supylabel("Works published per year (number)", fontsize=9.5)
    figure.supxlabel("Publication year", fontsize=9.5)
    figure.text(
        0.01, -0.03,
        "Each panel has its own vertical scale: compare shapes, not heights. "
        f"Hollow marker: {last_year}, the latest year. Panels are sorted by growth relative to the field; "
        "\"emerging\" sub-topics had too few works at the start to compute a growth rate.\n"
        + source_note(trends_config, fetch_date),
        fontsize=8, color=MUTED, ha="left", va="top",
    )
    figure.tight_layout(rect=(0.01, 0, 1, 0.97))
    return figure


def place_labels(figure: Figure, axes, texts: list[tuple[str, float, float]]) -> None:
    """Write a label next to each point without covering other labels or points.

    For each point, four positions are tried in turn (right, left, above,
    below). The first one that stays inside the plot and overlaps nothing
    already drawn is used. If none is free, the label goes to the right.
    The result is the same on every run: the order of points and positions
    is fixed.
    """
    positions = [
        dict(xytext=(9, 4), ha="left", va="bottom"),
        dict(xytext=(-9, 4), ha="right", va="bottom"),
        dict(xytext=(0, 10), ha="center", va="bottom"),
        dict(xytext=(0, -10), ha="center", va="top"),
    ]
    renderer = figure.canvas.get_renderer()
    frame = axes.get_window_extent(renderer)
    taken = []
    for _, x, y in texts:  # every marker is an obstacle for every label
        centre_x, centre_y = axes.transData.transform((x, y))
        taken.append(Bbox.from_extents(centre_x - 8, centre_y - 8, centre_x + 8, centre_y + 8))

    # The line at zero is an obstacle too, so no label is struck through by it.
    _, zero_y = axes.transData.transform((1, 0))
    taken.append(Bbox.from_extents(frame.x0, zero_y - 2, frame.x1, zero_y + 2))

    for label, x, y in texts:
        chosen = None
        for position in positions:
            note = axes.annotate(label, (x, y), textcoords="offset points", fontsize=9.5, color=INK, **position)
            box = note.get_window_extent(renderer)
            inside = frame.x0 <= box.x0 and box.x1 <= frame.x1 and frame.y0 <= box.y0 and box.y1 <= frame.y1
            if inside and not any(box.overlaps(other) for other in taken):
                chosen = box
                break
            note.remove()
        if chosen is None:
            note = axes.annotate(label, (x, y), textcoords="offset points", fontsize=9.5, color=INK, **positions[0])
            chosen = note.get_window_extent(renderer)
        taken.append(chosen)


def plot_trend_map(results: pd.DataFrame, trends_config: dict, fetch_date: str) -> Figure:
    """Volume against growth relative to the field (method note, section 6.2).

    Horizontal axis: works in the last three years, on a logarithmic scale.
    Vertical axis: relative momentum in percentage points; the line at 0
    means "growing exactly as fast as the field".
    Filled marker: the result is robust. Hollow marker: it is not, or could
    not be tested. Emerging sub-topics have no growth rate and are listed
    in a box beside the plot.
    """
    labels = labels_by_id(trends_config)
    last_year = trends_config["last_year"]
    rated = results[~results["emerging"]]
    emerging = results[results["emerging"]]

    figure, axes = plt.subplots(figsize=(11, 6.2))
    figure.subplots_adjust(left=0.08, right=0.70, top=0.86, bottom=0.20)

    axes.set_xscale("log")
    if len(rated) > 0:
        # Room on both sides, so labels fit inside the plot.
        axes.set_xlim(rated["volume"].min() / 1.8, rated["volume"].max() * 1.8)
        low, high = rated["relative_momentum"].min() * 100, rated["relative_momentum"].max() * 100
        padding = max(4.0, (high - low) * 0.2)
        axes.set_ylim(min(low, 0) - padding, max(high, 0) + padding)
        axes.axvline(rated["volume"].median(), color=MUTED, linewidth=1, linestyle=":")
    axes.axhline(0, color=MUTED, linewidth=1)
    # Plain numbers on the logarithmic axis (1,000 instead of 10^3).
    axes.xaxis.set_major_locator(ticker.LogLocator(base=10, subs=(1, 2, 3, 5)))
    axes.xaxis.set_major_formatter(ticker.FuncFormatter(lambda value, _: f"{value:,.0f}"))
    axes.xaxis.set_minor_formatter(ticker.NullFormatter())

    texts = []
    for row in rated.itertuples():
        points = row.relative_momentum * 100
        robust = row.robustness == "robust"
        axes.plot(
            row.volume, points, "o", markersize=9, color=INK,
            markerfacecolor=INK if robust else "white", markeredgewidth=1.5,
        )
        label = labels[row.subtopic_id]
        if not pd.isna(row.adoption_level):
            label += f" (adoption {int(row.adoption_level)})"
        if not row.passes_quality:
            label += " (search unreliable)"
        texts.append((label, row.volume, points))
    place_labels(figure, axes, texts)

    # Name the four areas in the corners of the plot.
    corner = dict(transform=axes.transAxes, fontsize=9, color=MUTED, style="italic")
    axes.text(0.02, 0.97, "Rising niche", va="top", ha="left", **corner)
    axes.text(0.98, 0.97, "Growing core", va="top", ha="right", **corner)
    axes.text(0.02, 0.03, "Fading or stable niche", va="bottom", ha="left", **corner)
    axes.text(0.98, 0.03, "Maturing core", va="bottom", ha="right", **corner)

    first_volume_year = last_year - trends_config["volume_window_years"] + 1
    axes.set_xlabel(f"Volume: works published {first_volume_year} to {last_year} (number, logarithmic scale)")
    axes.set_ylabel("Growth relative to the field (percentage points per year)")
    axes.spines[["top", "right"]].set_visible(False)
    figure.suptitle(
        "AI in industrial manufacturing: which sub-topics outgrow the field?",
        x=0.01, ha="left", fontsize=13, fontweight="bold",
    )

    # The box for emerging sub-topics, beside the plot.
    lines = ["Emerging: no growth rate", f"(works in {last_year}, 3-year volume)", ""]
    for row in emerging.sort_values("volume", ascending=False).itertuples():
        mark = "rising" if row.rising_three_years else "not rising every year"
        lines.append(f"{labels[row.subtopic_id]}")
        lines.append(f"   {int(row.works_end)} in {last_year}, {int(row.volume)} in 3 years; {mark}")
    if len(emerging) == 0:
        lines.append("none")
    figure.text(
        0.72, 0.84, "\n".join(lines), fontsize=9, color=INK, va="top", ha="left", linespacing=1.5,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor=MUTED),
    )

    start_year = last_year - trends_config["growth_window_years"]
    figure.text(
        0.01, 0.02,
        f"Growth is the compound annual rate {start_year} to {last_year}, minus the same rate for the whole field. "
        "Horizontal line: grows as fast as the field. Dotted line: median volume.\n"
        "Filled marker: same side of the line in both robustness tests. Hollow marker: side changes, or a test "
        f"could not be run. A sub-topic is \"emerging\" with fewer than {trends_config['emerging_threshold']} works in {start_year}.\n"
        + source_note(trends_config, fetch_date),
        fontsize=8, color=MUTED, ha="left", va="bottom",
    )
    return figure
