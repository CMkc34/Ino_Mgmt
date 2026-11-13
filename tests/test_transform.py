"""Tests for pipelines/transform.py.

Each test gives a function a small, fixed input and checks the result
against a value worked out by hand.

The trend metric tests all use one small made-up table (see example_counts),
built so that every case of the method occurs once.
"""

import pandas as pd
import pytest

from pipelines import transform
from pipelines.transform import compound_annual_growth_rate


def test_growth_rate_doubling_in_one_year_is_100_percent():
    assert compound_annual_growth_rate(100, 200, years=1) == pytest.approx(1.0)


def test_growth_rate_doubling_in_five_years():
    # 2 ** (1/5) - 1 = 0.1487
    assert compound_annual_growth_rate(100, 200, years=5) == pytest.approx(0.1487, abs=1e-4)


def test_growth_rate_is_negative_when_the_value_shrinks():
    assert compound_annual_growth_rate(200, 100, years=1) == pytest.approx(-0.5)


def test_growth_rate_rejects_a_zero_start_value():
    with pytest.raises(ValueError):
        compound_annual_growth_rate(0, 100, years=5)


def test_growth_rate_rejects_zero_years():
    with pytest.raises(ValueError):
        compound_annual_growth_rate(100, 200, years=0)


# --- the trend metrics ------------------------------------------------------
#
# The example. Field momentum by hand: (2000 / 1000) ** (1/5) - 1 = 0.1487.
#
#   sub-topic   2018 2019  2020  2021  2022  2023  2024  2025   what it shows
#   _field       800  900  1000  1200  1400  1600  1800  2000
#   topic_a       70   80   100   150   200   250   300   400   grows faster than the field
#   topic_b       50   50    50    55    60    60    55    50   flat: falls behind the field
#   topic_c        2    5    10    15    25    40    90   200   emerging: start under 30
#   topic_d       30   30    30    30    30    30    30    30   exactly at the threshold
#   topic_e       20   25    40    60    90   120   130   170   fine in 2020, too small in 2019

EXAMPLE = {
    "_field": [800, 900, 1000, 1200, 1400, 1600, 1800, 2000],
    "topic_a": [70, 80, 100, 150, 200, 250, 300, 400],
    "topic_b": [50, 50, 50, 55, 60, 60, 55, 50],
    "topic_c": [2, 5, 10, 15, 25, 40, 90, 200],
    "topic_d": [30, 30, 30, 30, 30, 30, 30, 30],
    "topic_e": [20, 25, 40, 60, 90, 120, 130, 170],
}
EXAMPLE_YEARS = list(range(2018, 2026))
EXAMPLE_CONFIG = {
    "last_year": 2025,
    "volume_window_years": 3,
    "growth_window_years": 5,
    "emerging_threshold": 30,
    "quality_threshold": 0.70,
}


def example_counts(data: dict = EXAMPLE) -> pd.DataFrame:
    """The example in the snapshot format: one row per sub-topic and year."""
    rows = [
        {"subtopic_id": subtopic_id, "year": year, "works_count": count}
        for subtopic_id, counts in data.items()
        for year, count in zip(EXAMPLE_YEARS, counts)
    ]
    return pd.DataFrame(rows)


def example_metrics(**options) -> pd.DataFrame:
    return transform.compute_trend_metrics(example_counts(), EXAMPLE_CONFIG, **options).set_index("subtopic_id")


def test_volume_is_the_sum_of_the_last_three_years():
    assert example_metrics().loc["topic_a", "volume"] == 250 + 300 + 400


def test_share_is_volume_divided_by_the_field_volume():
    assert example_metrics().loc["topic_a", "share"] == pytest.approx(950 / 5400)


def test_momentum_matches_the_hand_calculation():
    # (400 / 100) ** (1/5) - 1 = 0.3195
    assert example_metrics().loc["topic_a", "momentum"] == pytest.approx(0.3195, abs=1e-4)


def test_relative_momentum_is_the_difference_to_the_field():
    # 0.3195 - 0.1487 = 0.1708
    assert example_metrics().loc["topic_a", "relative_momentum"] == pytest.approx(0.1708, abs=1e-4)


def test_a_flat_subtopic_falls_behind_a_growing_field():
    metrics = example_metrics()
    assert metrics.loc["topic_b", "momentum"] == pytest.approx(0.0)
    assert metrics.loc["topic_b", "relative_momentum"] == pytest.approx(-0.1487, abs=1e-4)


def test_a_small_start_value_gives_the_emerging_flag_and_no_growth_rate():
    metrics = example_metrics()
    assert metrics.loc["topic_c", "emerging"]
    assert pd.isna(metrics.loc["topic_c", "momentum"])
    assert pd.isna(metrics.loc["topic_c", "relative_momentum"])
    assert metrics.loc["topic_c", "volume"] == 330  # volume is still reported


def test_exactly_at_the_threshold_is_not_emerging():
    metrics = example_metrics()
    assert not metrics.loc["topic_d", "emerging"]
    assert metrics.loc["topic_d", "momentum"] == pytest.approx(0.0)


def test_the_field_is_not_part_of_the_result():
    assert "_field" not in example_metrics().index


def test_a_missing_year_stops_the_calculation():
    counts = example_counts()
    broken = counts[~((counts["subtopic_id"] == "topic_a") & (counts["year"] == 2022))]
    with pytest.raises(ValueError, match="missing year"):
        transform.compute_trend_metrics(broken, EXAMPLE_CONFIG)


def test_a_snapshot_without_the_field_stops_the_calculation():
    counts = example_counts()
    with pytest.raises(ValueError, match="_field"):
        transform.compute_trend_metrics(counts[counts["subtopic_id"] != "_field"], EXAMPLE_CONFIG)


# --- robustness tests A and B -----------------------------------------------


def test_shifted_window_uses_the_years_one_step_back():
    # Test A, 2019 to 2024. Field: (1800 / 900) ** (1/5) - 1 = 0.1487.
    # topic_a: (300 / 80) ** (1/5) - 1 = 0.3026, so relative +0.1539.
    shifted = example_metrics(shift_years=1)
    assert shifted.loc["topic_a", "relative_momentum"] == pytest.approx(0.1539, abs=1e-4)


def test_smoothed_ends_use_two_year_averages():
    # Test B. Field: 950 -> 1900, still 0.1487.
    # topic_a: 90 -> 350, (350 / 90) ** (1/5) - 1 = 0.3121, so relative +0.1634.
    smoothed = example_metrics(smooth=True)
    assert smoothed.loc["topic_a", "relative_momentum"] == pytest.approx(0.1634, abs=1e-4)


def test_volume_does_not_move_with_the_shifted_window():
    assert example_metrics(shift_years=1).loc["topic_a", "volume"] == 950


def test_emerging_rule_follows_the_window_in_use():
    # topic_e has 40 works in 2020 (fine) but 25 in 2019 (too small).
    assert not example_metrics().loc["topic_e", "emerging"]
    assert example_metrics(shift_years=1).loc["topic_e", "emerging"]


@pytest.mark.parametrize(
    "main, shifted, smoothed, expected",
    [
        (0.10, 0.05, 0.08, "robust"),
        (-0.10, -0.05, -0.08, "robust"),
        (0.10, -0.05, 0.08, "not robust"),
        (0.10, 0.05, -0.01, "not robust"),
        (0.10, float("nan"), 0.08, "not testable"),
        (float("nan"), float("nan"), float("nan"), "emerging"),
    ],
)
def test_robustness_label(main, shifted, smoothed, expected):
    assert transform.robustness_label(main, shifted, smoothed) == expected


# --- the full result table --------------------------------------------------


def example_quality() -> pd.DataFrame:
    """Quality check results: topic_b fails, and topic_a has two raters."""
    rows = [
        ("topic_a", 0, 20, 8, "first"),    # an early round that must be ignored
        ("topic_a", 1, 20, 19, "first"),
        ("topic_a", 1, 20, 17, "second"),  # the lower share of the last round counts
        ("topic_b", 0, 20, 10, "first"),
        ("topic_c", 0, 20, 16, "first"),
        ("topic_d", 0, 20, 18, "first"),
        ("topic_e", 0, 20, 18, "first"),
    ]
    return pd.DataFrame(rows, columns=["subtopic_id", "round", "sample_size", "relevant", "rater"])


def example_results(**options) -> pd.DataFrame:
    results = transform.build_trend_results(example_counts(), EXAMPLE_CONFIG, example_quality(), **options)
    return results.set_index("subtopic_id")


def test_quality_share_takes_the_last_round_and_the_lowest_rater():
    shares = transform.quality_shares(example_quality())
    assert shares["topic_a"] == pytest.approx(17 / 20)
    assert shares["topic_b"] == pytest.approx(0.5)


def test_robustness_labels_in_the_result_table():
    results = example_results()
    assert results.loc["topic_a", "robustness"] == "robust"
    assert results.loc["topic_b", "robustness"] == "robust"  # below the field in all three
    assert results.loc["topic_c", "robustness"] == "emerging"
    assert results.loc["topic_e", "robustness"] == "not testable"


def test_shortlist_rule():
    results = example_results()
    # Above the field, robust, passes the quality check.
    assert results.loc["topic_a", "on_shortlist_by_rule"]
    # Below the field.
    assert not results.loc["topic_d", "on_shortlist_by_rule"]
    # Emerging and rising in each of the last three years.
    assert results.loc["topic_c", "rising_three_years"]
    assert results.loc["topic_c", "on_shortlist_by_rule"]
    # Above the field, but the result could not be tested for robustness.
    assert results.loc["topic_e", "relative_momentum"] > 0
    assert not results.loc["topic_e", "on_shortlist_by_rule"]


def test_a_failed_quality_check_keeps_a_subtopic_off_the_shortlist():
    data = dict(EXAMPLE, topic_b=EXAMPLE["topic_a"])  # give topic_b the strong numbers of topic_a
    results = transform.build_trend_results(example_counts(data), EXAMPLE_CONFIG, example_quality())
    results = results.set_index("subtopic_id")
    assert results.loc["topic_b", "relative_momentum"] > 0
    assert not results.loc["topic_b", "passes_quality"]
    assert not results.loc["topic_b", "on_shortlist_by_rule"]


def test_variant_data_sets_add_their_own_column():
    results = example_results(variant_counts={"no_ai": example_counts()})
    assert results.loc["topic_a", "relative_momentum_no_ai"] == pytest.approx(0.1708, abs=1e-4)


def test_adoption_level_is_empty_until_it_is_filled_in():
    assert example_results()["adoption_level"].isna().all()
    adoption = pd.DataFrame({"subtopic_id": ["topic_a"], "level": [2]})
    results = example_results(adoption=adoption)
    assert results.loc["topic_a", "adoption_level"] == 2
    assert pd.isna(results.loc["topic_b", "adoption_level"])


def test_results_are_sorted_strongest_first_with_emerging_last():
    order = list(transform.build_trend_results(example_counts(), EXAMPLE_CONFIG, example_quality())["subtopic_id"])
    # topic_e grows fastest: (170 / 40) ** (1/5) - 1 = 0.336, ahead of topic_a at 0.320.
    assert order[:2] == ["topic_e", "topic_a"]
    assert order[-1] == "topic_c"


# --- the discovery step -----------------------------------------------------


def example_topics() -> pd.DataFrame:
    rows = [
        ("T1", "Fast and large enough", 40, 400),      # (400/40) ** (1/5) - 1 = 0.585
        ("T2", "Slower", 100, 200),                    # 0.149
        ("T3", "Too small at the start", 10, 500),     # under the threshold of 30
        ("T4", "No count for the last year", 80, None),
        ("T5", "No count for the first year", None, 300),
        ("T6", "Middle", 50, 200),                     # 0.320
    ]
    return pd.DataFrame(rows, columns=["topic_id", "topic_name", "works_first_year", "works_last_year"])


DISCOVERY_CONFIG = dict(EXAMPLE_CONFIG, discovery_top_n=2)


def test_discovery_ranks_eligible_labels_by_growth_and_keeps_the_top_n():
    ranking = transform.discovery_ranking(example_topics(), 0.1487, DISCOVERY_CONFIG)
    assert list(ranking["topic_id"]) == ["T1", "T6"]
    assert ranking.loc[0, "momentum"] == pytest.approx(0.585, abs=1e-3)
    assert ranking.loc[0, "relative_momentum"] == pytest.approx(0.585 - 0.1487, abs=1e-3)


def test_discovery_leaves_out_small_and_incomplete_labels():
    config = dict(EXAMPLE_CONFIG, discovery_top_n=10)
    ranked = set(transform.discovery_ranking(example_topics(), 0.1487, config)["topic_id"])
    assert ranked == {"T1", "T2", "T6"}


def test_discovery_adds_the_mapping_to_the_subtopics():
    mapping = pd.DataFrame(
        {"topic_id": ["T1"], "closest_subtopic": ["topic_a"], "comment": ["same area"]}
    )
    ranking = transform.discovery_ranking(example_topics(), 0.1487, DISCOVERY_CONFIG, mapping=mapping)
    assert ranking.loc[0, "closest_subtopic"] == "topic_a"
    assert pd.isna(ranking.loc[1, "closest_subtopic"])  # T6 is not in the mapping yet
