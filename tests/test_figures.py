"""Tests for pipelines/figures.py."""

import io

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

from pipelines import figures, transform
from pipelines.figures import save_figure


def simple_chart():
    figure, axes = plt.subplots()
    axes.plot([2023, 2024, 2025], [10, 20, 40])
    axes.set_title("Example")
    return figure


def test_saving_the_same_chart_twice_gives_identical_files(tmp_path):
    first = save_figure(simple_chart(), "example", tmp_path).read_bytes()
    second = save_figure(simple_chart(), "example", tmp_path).read_bytes()
    assert first == second


def recompressed(png: bytes) -> bytes:
    """The same picture, stored with a different compression setting."""
    picture = Image.open(io.BytesIO(png))
    stored = io.BytesIO()
    picture.save(stored, format="png", compress_level=1)
    return stored.getvalue()


def test_a_file_with_the_same_picture_is_left_untouched(tmp_path):
    # This is the situation on another computer: the chart file in the
    # repository shows the same picture but was compressed differently.
    path = save_figure(simple_chart(), "example", tmp_path)
    other_computer = recompressed(path.read_bytes())
    assert other_computer != path.read_bytes()
    path.write_bytes(other_computer)

    save_figure(simple_chart(), "example", tmp_path)
    assert path.read_bytes() == other_computer


def test_a_changed_picture_replaces_the_file(tmp_path):
    path = save_figure(simple_chart(), "example", tmp_path)
    before = path.read_bytes()

    changed, axes = plt.subplots()
    axes.plot([2023, 2024, 2025], [10, 20, 41])  # one value differs
    axes.set_title("Example")
    save_figure(changed, "example", tmp_path)
    assert path.read_bytes() != before


# --- the two trend scan charts ----------------------------------------------
#
# What a chart looks like cannot be tested by a program. These tests check
# that each chart can be drawn from a small table, contains the expected
# parts, and comes out identical on every run.

CONFIG = {
    "title": "Example field",
    "source": "OpenAlex",
    "last_year": 2025,
    "volume_window_years": 3,
    "growth_window_years": 5,
    "emerging_threshold": 30,
    "quality_threshold": 0.70,
    "subtopics": [
        {"id": "topic_a", "label": "Topic A (with an explanation)"},
        {"id": "topic_b", "label": "Topic B"},
        {"id": "topic_c", "label": "Topic C"},
    ],
}
YEARS = list(range(2019, 2026))
DATA = {
    "_field": [900, 1000, 1200, 1400, 1600, 1800, 2000],
    "topic_a": [80, 100, 150, 200, 250, 300, 400],
    "topic_b": [50, 50, 55, 60, 60, 55, 50],
    "topic_c": [5, 10, 15, 25, 40, 90, 200],  # emerging
}


def small_counts() -> pd.DataFrame:
    rows = [
        {"subtopic_id": subtopic_id, "year": year, "works_count": count}
        for subtopic_id, counts in DATA.items()
        for year, count in zip(YEARS, counts)
    ]
    return pd.DataFrame(rows)


def small_results() -> pd.DataFrame:
    quality = pd.DataFrame(
        {"subtopic_id": ["topic_a", "topic_b", "topic_c"], "round": 0, "sample_size": 20, "relevant": [18, 18, 18]}
    )
    return transform.build_trend_results(small_counts(), CONFIG, quality)


def all_text(figure) -> str:
    return " | ".join(text.get_text() for text in figure.findobj(plt.Text))


def test_short_label_drops_the_explanation_in_brackets():
    assert figures.short_label("Topic A (with an explanation)") == "Topic A"


def test_time_series_has_one_panel_per_subtopic_and_names_the_source():
    figure = figures.plot_time_series(small_counts(), small_results(), CONFIG, "2026-11-12")
    visible_panels = [panel for panel in figure.axes if panel.get_visible()]
    assert len(visible_panels) == 3
    text = all_text(figure)
    assert "Topic A" in text and "emerging" in text
    assert "Source: OpenAlex" in text and "2026-11-12" in text
    plt.close(figure)


def test_trend_map_labels_rated_subtopics_and_lists_emerging_ones_in_the_box():
    figure = figures.plot_trend_map(small_results(), CONFIG, "2026-11-12")
    axes = figure.axes[0]
    labels_in_plot = [text.get_text() for text in axes.texts]
    assert "Topic A" in labels_in_plot and "Topic B" in labels_in_plot
    assert "Topic C" not in labels_in_plot  # emerging: no point in the plot
    assert "Topic C" in all_text(figure)    # but listed in the box
    assert axes.get_xscale() == "log"
    assert "Source: OpenAlex" in all_text(figure)
    plt.close(figure)


def test_trend_map_shows_the_adoption_level_once_it_is_filled_in():
    results = small_results()
    results["adoption_level"] = pd.array([2, pd.NA, pd.NA], dtype="Int64")  # first row is topic_a
    figure = figures.plot_trend_map(results, CONFIG, "2026-11-12")
    assert "Topic A [2]" in [text.get_text() for text in figure.axes[0].texts]
    assert "In square brackets: adoption in industry" in all_text(figure)
    plt.close(figure)


def test_trend_charts_come_out_identical_on_every_run(tmp_path):
    def draw(name):
        if name == "map":
            return figures.plot_trend_map(small_results(), CONFIG, "2026-11-12")
        return figures.plot_time_series(small_counts(), small_results(), CONFIG, "2026-11-12")

    for name in ("map", "series"):
        first = save_figure(draw(name), name, tmp_path).read_bytes()
        second = save_figure(draw(name), name, tmp_path).read_bytes()
        assert first == second


# --- the two scoring charts -------------------------------------------------


def small_ranking() -> tuple[pd.DataFrame, dict]:
    from tests.test_scoring import CONFIG, opportunities, scores
    from pipelines import scoring

    config = dict(CONFIG, data_label="Made-up example data.")
    return scoring.build_ranking(opportunities(), scores(), config), config


def test_rank_stability_chart_has_one_bar_per_opportunity_and_names_the_class():
    ranking, config = small_ranking()
    figure = figures.plot_rank_stability(ranking, config)
    assert len(figure.axes[0].patches) == len(ranking)
    text = all_text(figure)
    assert "pursue" in text and "park" in text
    assert "Made-up example data." in text and "illustrative" in text
    plt.close(figure)


def test_time_horizon_chart_labels_every_opportunity_and_is_marked_illustrative():
    ranking, config = small_ranking()
    figure = figures.plot_time_horizon(ranking, config)
    text = all_text(figure)
    for name in ranking["name"]:
        assert name in text  # every opportunity is named in the key
    rank_labels = " ".join(label.get_text() for label in figure.axes[0].texts)
    for rank in ranking["rank"]:
        assert str(rank) in rank_labels  # and marked by its rank in the plot
    assert "illustrative" in text
    plt.close(figure)
