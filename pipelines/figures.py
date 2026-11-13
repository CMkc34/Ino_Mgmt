"""Step 3: charts.

Every chart goes through save_figure, so all figures share the same size
settings and are reproducible (acceptance criteria AC-1.3 and AC-2.4).

Chart rules for this project (requirement G-5): a title, labelled axes with
units, a source note, and never colour alone to tell series apart.
"""

import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to files; no window needed (works in CI too)

# Ignore any chart settings stored on this particular computer and use the
# font that ships with matplotlib. Otherwise the same code would draw
# different files on different machines.
matplotlib.rcdefaults()
matplotlib.rcParams["font.family"] = "DejaVu Sans"

import matplotlib.pyplot as plt  # noqa: E402  (must come after the line above)
from matplotlib import image  # noqa: E402
import matplotlib.ticker as ticker  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.transforms import Bbox  # noqa: E402

from pipelines.paths import FIGURES_DIR  # noqa: E402


def same_picture(first_png: bytes, second_png: bytes) -> bool:
    """True if two PNG files show exactly the same picture, pixel for pixel.

    Two files can hold the identical picture and still differ as files,
    because computers compress images in slightly different ways.
    """
    first = image.imread(io.BytesIO(first_png))
    second = image.imread(io.BytesIO(second_png))
    return first.shape == second.shape and bool((first == second).all())


def save_figure(figure: Figure, name: str, figures_dir: Path = FIGURES_DIR) -> Path:
    """Save a chart as PNG and return its path.

    The chart is drawn at a fixed size and resolution. If a file with the
    same picture already exists, it is left untouched. So a chart file only
    changes when the picture changes, and not because a different computer
    compressed it differently.

    The "Software" entry normally stores the matplotlib version inside the
    file. It is removed so the file does not change between versions.
    """
    figures_dir.mkdir(parents=True, exist_ok=True)
    path = figures_dir / f"{name}.png"

    drawn = io.BytesIO()
    figure.savefig(drawn, format="png", dpi=150, metadata={"Software": None})
    plt.close(figure)

    if not (path.exists() and same_picture(path.read_bytes(), drawn.getvalue())):
        path.write_bytes(drawn.getvalue())
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
    figure.supxlabel("Publication year", fontsize=9.5, y=0.11)
    figure.text(
        0.01, 0.015,
        "Each panel has its own vertical scale: compare shapes, not heights. "
        f"Hollow marker: {last_year}, the latest year. Panels are sorted by growth relative to the field; "
        "\"emerging\" sub-topics had too few works at the start to compute a growth rate.\n"
        + source_note(trends_config, fetch_date),
        fontsize=8, color=MUTED, ha="left", va="bottom",
    )
    # Leave room for the title above and the note below the panels.
    figure.tight_layout(rect=(0.01, 0.13, 1, 0.95))
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
    not be tested. A number in square brackets after a label is the adoption
    level, once data/manual/adoption.csv is filled in. Emerging sub-topics have no growth rate and are listed
    in a box beside the plot.
    """
    labels = labels_by_id(trends_config)
    last_year = trends_config["last_year"]
    rated = results[~results["emerging"]]
    emerging = results[results["emerging"]]

    figure, axes = plt.subplots(figsize=(12.5, 6.4))
    figure.subplots_adjust(left=0.07, right=0.64, top=0.88, bottom=0.235)

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
            label += f" [{int(row.adoption_level)}]"
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
        level = "" if pd.isna(row.adoption_level) else f" [{int(row.adoption_level)}]"
        lines.append(f"{labels[row.subtopic_id]}{level}")
        lines.append(f"   {int(row.works_end)} in {last_year}, {int(row.volume)} in 3 years; {mark}")
    if len(emerging) == 0:
        lines.append("none")
    figure.text(
        0.67, 0.86, "\n".join(lines), fontsize=9, color=INK, va="top", ha="left", linespacing=1.5,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor=MUTED),
    )

    start_year = last_year - trends_config["growth_window_years"]
    adoption_note = ""
    if results["adoption_level"].notna().any():
        adoption_note = (
            "In square brackets: adoption in industry, from 0 (no commercial offer found) and 1 (offered by vendors) "
            "to 2 (documented use at a named manufacturer) and 3 (widespread according to a survey).\n"
        )
    figure.text(
        0.01, 0.02,
        f"Growth is the compound annual rate {start_year} to {last_year}, minus the same rate for the whole field. "
        "Horizontal line: grows as fast as the field. Dotted line: median volume.\n"
        "Filled marker: same side of the line in both robustness tests. Hollow marker: side changes, or a test "
        f"could not be run. A sub-topic is \"emerging\" with fewer than {trends_config['emerging_threshold']} works in {start_year}.\n"
        + adoption_note
        + source_note(trends_config, fetch_date),
        fontsize=8, color=MUTED, ha="left", va="bottom",
    )
    return figure


# --- charts for the scoring model (method note, section 9) --------------------


def plot_rank_stability(ranking: pd.DataFrame, scoring_config: dict) -> Figure:
    """Horizontal bars: in what share of the runs is each opportunity in the top group?

    Bars follow the ranking, best total at the top. The two vertical lines
    are the limits of the classification rule. The class is written after
    each bar, so it does not depend on colour.
    """
    rules = scoring_config["rules"]
    figure, axes = plt.subplots(figsize=(12.5, 1.6 + 0.62 * len(ranking)))
    figure.subplots_adjust(left=0.40, right=0.84, top=0.80, bottom=0.30)

    positions = range(len(ranking))
    shares = ranking["top_share"] * 100
    axes.barh(positions, shares, color=INK, height=0.55)
    axes.set_yticks(positions)
    axes.set_yticklabels([f"{row.name}  (total {row.total:.2f})" for row in ranking.itertuples()], fontsize=9.5)
    axes.invert_yaxis()  # best total at the top
    axes.set_xlim(0, 100)
    for limit, text in ((rules["pursue_top_share"], "pursue from here"), (rules["park_top_share"], "park below")):
        axes.axvline(limit * 100, color=MUTED, linewidth=1, linestyle=":")
        axes.text(limit * 100, -0.75, text, fontsize=8.5, color=MUTED, ha="center", va="bottom")
    for position, row in zip(positions, ranking.itertuples()):
        axes.text(101.5, position, f"{row.top_share * 100:.0f}%   {row.classification}", fontsize=9.5, va="center", color=INK)

    axes.set_xlabel(f"Share of {scoring_config['sensitivity_runs']:,} runs with varied weights in which it is in the top {rules['top_n']} (%)")
    axes.spines[["top", "right"]].set_visible(False)
    figure.suptitle("How stable is the ranking when the weights change?", x=0.01, ha="left", fontsize=13, fontweight="bold")
    figure.text(
        0.01, 0.02,
        f"Each weight was varied by up to {scoring_config['weight_variation'] * 100:.0f}% at random. "
        f"Pursue also needs a total of at least {rules['pursue_min_total']} and no score of 1; "
        f"a total below {rules['park_max_total']} means park.\n"
        f"Scores are judgements for an illustrative reference organisation. {scoring_config['data_label']}",
        fontsize=8, color=MUTED, ha="left", va="bottom",
    )
    return figure


def plot_time_horizon(ranking: pd.DataFrame, scoring_config: dict) -> Figure:
    """Scatter: time to first value against the score on all other criteria.

    Time to value is left out of the vertical axis because it is already the
    horizontal one. The three bands are the time horizons.
    """
    figure, axes = plt.subplots(figsize=(12.5, 6))
    figure.subplots_adjust(left=0.07, right=0.60, top=0.86, bottom=0.21)

    bands = ((0, 12, "under 12 months"), (12, 36, "12 to 36 months"), (36, 48, "over 36 months"))
    for index, (start, end, text) in enumerate(bands):
        if index % 2 == 0:
            axes.axvspan(start, end, color="#f0f0f0", zorder=0)
        axes.text((start + end) / 2, 5.05, text, fontsize=9, color=MUTED, ha="center", va="bottom")

    # Each point is labelled with its rank; the names are in the key beside
    # the plot. Opportunities at the same position share one point.
    positioned = ranking.assign(height=ranking["score_without_time"].round(3))
    texts = []
    for (months, height), group in positioned.groupby(["months_to_value", "height"], sort=True):
        axes.plot(months, height, "o", markersize=9, color=INK)
        texts.append((" / ".join(str(rank) for rank in group["rank"]), months, height))
    axes.set_xlim(0, 48)
    axes.set_ylim(1, 5)
    place_labels(figure, axes, texts)

    key = ["Rank, opportunity and class", ""]
    for row in ranking.itertuples():
        key.append(f"{row.rank}  {row.name}")
        key.append(f"     total {row.total:.2f}; {row.classification}")
    figure.text(
        0.62, 0.86, "\n".join(key), fontsize=8.5, color=INK, va="top", ha="left", linespacing=1.45,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor=MUTED),
    )

    axes.set_xlabel("Time to first measurable value (months, midpoint of the scored band)")
    axes.set_ylabel("Score on the other criteria (1 to 5)")
    axes.spines[["top", "right"]].set_visible(False)
    figure.suptitle("How good, and how soon?", x=0.01, ha="left", fontsize=13, fontweight="bold")
    figure.text(
        0.01, 0.02,
        "Numbers are ranks by total score. Vertical axis: weighted score without the time criterion, weights rescaled to sum to 1.\n"
        "The Three Horizons framework covers more than time; the bands only show the time dimension.\n"
        f"Scores are judgements for an illustrative reference organisation. {scoring_config['data_label']}",
        fontsize=8, color=MUTED, ha="left", va="bottom",
    )
    return figure
