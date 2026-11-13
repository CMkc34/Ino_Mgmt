"""Step 2: turn raw counts into the metrics used in the analysis.

Functions here take tables in and give tables (or numbers) out. They do not
read or write files, which makes them easy to test with small fixed inputs
(requirement R-1.8).
"""

import pandas as pd


def compound_annual_growth_rate(first_value: float, last_value: float, years: int) -> float:
    """Average yearly growth rate that turns first_value into last_value.

    Example: 100 works growing to 200 works over 5 years is about 14.9% a
    year, because 100 * 1.149 ** 5 is roughly 200.

    This function is complete and tested. Use it as the pattern for the
    functions below.
    """
    if years <= 0:
        raise ValueError("years must be greater than 0")
    if first_value <= 0:
        raise ValueError("first_value must be greater than 0")
    return (last_value / first_value) ** (1 / years) - 1


FIELD_ID = "_field"  # the sub-topic id that holds the counts of the whole field


def yearly_table(counts: pd.DataFrame) -> pd.DataFrame:
    """Reshape the snapshot: one row per sub-topic, one column per year.

    The snapshot has one row per sub-topic AND year. Here each sub-topic
    becomes a single row, so "works of X in year Y" is a simple lookup.
    Stops if a year is missing for any sub-topic, because that means the
    snapshot is broken.
    """
    table = counts.pivot(index="subtopic_id", columns="year", values="works_count")
    if table.isna().any().any():
        raise ValueError("the snapshot has a missing year for at least one sub-topic")
    if FIELD_ID not in table.index:
        raise ValueError(f"the snapshot has no row for the field ('{FIELD_ID}')")
    return table


def growth_rates(
    table: pd.DataFrame,
    start_years: list[int],
    end_years: list[int],
    steps: int,
    threshold: float,
) -> pd.Series:
    """Compound annual growth rate per sub-topic, or empty where the start is too small.

    start_years / end_years   the start and end value are the AVERAGE of these
                              years. One year each gives the plain rate; two
                              years each give the "smoothed" rate.
    steps                     number of yearly steps between start and end
    threshold                 if the start value is below this, no rate is
                              computed and the cell stays empty. A rate from a
                              tiny start value would be meaningless.

    The field itself is always computed, whatever its start value.
    """
    start = table[start_years].mean(axis=1)
    end = table[end_years].mean(axis=1)

    rates = pd.Series(float("nan"), index=table.index)
    for subtopic_id in table.index:
        if subtopic_id == FIELD_ID or start[subtopic_id] >= threshold:
            rates[subtopic_id] = compound_annual_growth_rate(start[subtopic_id], end[subtopic_id], steps)
    return rates


def compute_trend_metrics(counts: pd.DataFrame, trends_config: dict, shift_years: int = 0, smooth: bool = False) -> pd.DataFrame:
    """Volume, share, momentum and relative momentum for each sub-topic.

    Definitions: docs/design/trend-scan-method.md, section 4.

    Input:  the snapshot table (subtopic_id, year, works_count).
    Output: one row per sub-topic (without the field), with the columns
        works_start        works at the start of the growth window
        works_end          works at the end of the growth window
        volume             works in the last `volume_window_years` years
        share              volume divided by the field's volume
        emerging           True if works_start is below `emerging_threshold`
        momentum           compound annual growth over the growth window
        relative_momentum  momentum minus the field's momentum

    For an emerging sub-topic, momentum and relative_momentum are empty.

    The two optional arguments give the robustness tests of section 7:
        shift_years=1   test A: the growth window is moved one year back
        smooth=True     test B: start and end are each the average of two
                        years (the window's year and the year before it)
    The emerging rule always looks at the start value of the window in use.
    Volume and share are always taken from the last years of the data.
    """
    table = yearly_table(counts)
    last_year = trends_config["last_year"]
    steps = trends_config["growth_window_years"]
    threshold = trends_config["emerging_threshold"]

    end_year = last_year - shift_years
    start_year = end_year - steps
    if smooth:
        start_years, end_years = [start_year - 1, start_year], [end_year - 1, end_year]
    else:
        start_years, end_years = [start_year], [end_year]
    missing = [year for year in start_years + end_years if year not in table.columns]
    if missing:
        raise ValueError(f"the snapshot does not contain the years {missing}")

    momentum = growth_rates(table, start_years, end_years, steps, threshold)

    volume_years = [last_year - offset for offset in range(trends_config["volume_window_years"])]
    volume = table[volume_years].sum(axis=1)

    metrics = pd.DataFrame(
        {
            "works_start": table[start_years].mean(axis=1),
            "works_end": table[end_years].mean(axis=1),
            "volume": volume,
            "share": volume / volume[FIELD_ID],
            "emerging": table[start_years].mean(axis=1) < threshold,
            "momentum": momentum,
            "relative_momentum": momentum - momentum[FIELD_ID],
        }
    )
    metrics = metrics.drop(index=FIELD_ID)  # the field is the yardstick, not a result
    return metrics.reset_index()


def robustness_label(main: float, shifted: float, smoothed: float) -> str:
    """Say whether a sub-topic stays on the same side of the field in tests A and B.

    "robust"        above the field in all three, or below in all three
    "not robust"    the side changes in test A or test B
    "not testable"  the main result exists, but test A or B has no rate
                    because its start value is under the emerging threshold
    "emerging"      there is no main result to test
    """
    if pd.isna(main):
        return "emerging"
    if pd.isna(shifted) or pd.isna(smoothed):
        return "not testable"
    same_side = (main > 0) == (shifted > 0) == (smoothed > 0)
    return "robust" if same_side else "not robust"


def rose_every_year(table: pd.DataFrame, last_year: int, years: int = 3) -> pd.Series:
    """True for a sub-topic whose yearly count rose in each of the last `years` years."""
    rising = pd.Series(True, index=table.index)
    for year in range(last_year - years + 1, last_year + 1):
        rising &= table[year] > table[year - 1]
    return rising


def quality_shares(quality: pd.DataFrame) -> pd.Series:
    """Share of relevant works per sub-topic from the query-quality check.

    Uses the last round of each sub-topic. If several raters rated that
    round, the LOWEST share counts, which is the cautious reading.
    """
    quality = quality.assign(share=quality["relevant"] / quality["sample_size"])
    last_round = quality.groupby("subtopic_id")["round"].transform("max")
    return quality[quality["round"] == last_round].groupby("subtopic_id")["share"].min()


def build_trend_results(
    counts: pd.DataFrame,
    trends_config: dict,
    quality: pd.DataFrame,
    variant_counts: dict[str, pd.DataFrame] | None = None,
    adoption: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """The full result table of the trend scan: metrics, robustness tests, shortlist rule.

    Adds to the metrics of compute_trend_metrics:
        relative_momentum_shifted   test A (window one year back)
        relative_momentum_smoothed  test B (two-year averages)
        robustness                  see robustness_label
        relative_momentum_<name>    the main calculation on each variant data
                                    set (test C "articles", test D "no_ai")
        quality_share               from the query-quality check
        passes_quality              quality_share reaches `quality_threshold`
        rising_three_years          count rose in each of the last three years
        on_shortlist_by_rule        rules 1 to 3 of the method note, section 8
        adoption_level              from data/manual/adoption.csv, if filled in

    Shortlist rule: a sub-topic that passes the quality check is listed if
      - its relative momentum is above 0 and "robust", or
      - it is emerging and its count rose in each of the last three years.
    Rules 4 and 5 (one justified exception; at most eight) need judgement and
    are applied in the write-up.
    """
    results = compute_trend_metrics(counts, trends_config).set_index("subtopic_id")

    shifted = compute_trend_metrics(counts, trends_config, shift_years=1).set_index("subtopic_id")
    smoothed = compute_trend_metrics(counts, trends_config, smooth=True).set_index("subtopic_id")
    results["relative_momentum_shifted"] = shifted["relative_momentum"]
    results["relative_momentum_smoothed"] = smoothed["relative_momentum"]
    results["robustness"] = [
        robustness_label(main, a, b)
        for main, a, b in zip(
            results["relative_momentum"], results["relative_momentum_shifted"], results["relative_momentum_smoothed"]
        )
    ]

    for name, other_counts in (variant_counts or {}).items():
        other = compute_trend_metrics(other_counts, trends_config).set_index("subtopic_id")
        results[f"relative_momentum_{name}"] = other["relative_momentum"]

    results["quality_share"] = quality_shares(quality).reindex(results.index)
    results["passes_quality"] = results["quality_share"] >= trends_config["quality_threshold"]

    table = yearly_table(counts)
    results["rising_three_years"] = rose_every_year(table, trends_config["last_year"]).reindex(results.index)

    above_and_robust = (results["relative_momentum"] > 0) & (results["robustness"] == "robust")
    emerging_and_rising = results["emerging"] & results["rising_three_years"]
    results["on_shortlist_by_rule"] = results["passes_quality"] & (above_and_robust | emerging_and_rising)

    if adoption is not None and len(adoption) > 0:
        results["adoption_level"] = adoption.set_index("subtopic_id")["level"].reindex(results.index).astype("Int64")
    else:
        results["adoption_level"] = pd.array([pd.NA] * len(results), dtype="Int64")

    # Strongest result first; emerging sub-topics (no rate) after that, largest first.
    results = results.reset_index()
    results = results.sort_values(
        ["emerging", "relative_momentum", "volume"], ascending=[True, False, False], kind="stable"
    )
    return results.reset_index(drop=True)


def discovery_ranking(
    topics: pd.DataFrame,
    field_momentum: float,
    trends_config: dict,
    mapping: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """The fastest-growing topic labels of the source within the field (method note, section 6.4).

    Input:  the discovery table (topic_id, topic_name, works_first_year,
            works_last_year), counted for the two ends of the growth window.
    Output: the `discovery_top_n` labels with the strongest growth, with
        momentum            compound annual growth over the window
        relative_momentum   momentum minus the field's momentum
        closest_subtopic    which of the sub-topics the label corresponds to,
        comment             or "none"; both from the hand-made mapping file

    A label is only ranked if it has at least `emerging_threshold` works in
    the first year (the same rule as for sub-topics) and a count for the
    last year. Labels are the source's own classification of each work.
    """
    steps = trends_config["growth_window_years"]
    eligible = topics[
        (topics["works_first_year"] >= trends_config["emerging_threshold"]) & topics["works_last_year"].notna()
    ].copy()
    eligible["momentum"] = [
        compound_annual_growth_rate(first, last, steps)
        for first, last in zip(eligible["works_first_year"], eligible["works_last_year"])
    ]
    eligible["relative_momentum"] = eligible["momentum"] - field_momentum
    # Strongest growth first; the id breaks ties, so the order is always the same.
    eligible = eligible.sort_values(["momentum", "topic_id"], ascending=[False, True])
    ranking = eligible.head(trends_config["discovery_top_n"]).reset_index(drop=True)

    if mapping is not None:
        ranking = ranking.merge(mapping[["topic_id", "closest_subtopic", "comment"]], on="topic_id", how="left")
    else:
        ranking["closest_subtopic"] = pd.NA
        ranking["comment"] = pd.NA
    return ranking
