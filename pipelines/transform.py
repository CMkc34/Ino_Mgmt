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


def compute_trend_metrics(counts: pd.DataFrame, trends_config: dict) -> pd.DataFrame:
    """Compute volume, momentum and relative momentum for each sub-topic.

    TODO (owner, sprint 1): implement this (requirement R-2.4).

    Input:  the snapshot table (subtopic_id, year, works_count).
    Output: one row per sub-topic with the columns
            subtopic_id, volume, momentum, relative_momentum.

    Definitions:
      - volume: works in the last `volume_window_years` complete years.
      - momentum: compound annual growth over the last `growth_window_years`.
      - relative_momentum: the sub-topic's momentum minus the momentum of
        the whole field (sub-topic id "_field").

    Decide and document what happens when a sub-topic has zero works in the
    first year of the growth window.
    """
    raise NotImplementedError(
        "compute_trend_metrics is not written yet. See the TODO in pipelines/transform.py."
    )
