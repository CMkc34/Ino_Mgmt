"""Tests for pipelines/scoring.py.

All tests use one small made-up set of five opportunities, built so that
every rule of the model applies once. Totals by hand, with the weights
0.25 / 0.25 / 0.20 / 0.15 / 0.15:

    A   5 4 5 3 4   ->  1.25 + 1.00 + 1.00 + 0.45 + 0.60 = 4.30
    B   4 5 3 5 4   ->  1.00 + 1.25 + 0.60 + 0.75 + 0.60 = 4.20   (within 0.25 of A)
    C   5 3 4 2 1   ->  1.25 + 0.75 + 0.80 + 0.30 + 0.15 = 3.25   (a score of 1)
    D   2 3 2 4 3   ->  0.50 + 0.75 + 0.40 + 0.60 + 0.45 = 2.70
    E   3 2 2 2 2   ->  0.75 + 0.50 + 0.40 + 0.30 + 0.30 = 2.25   (below 2.5)
"""

import pandas as pd
import pytest

from pipelines import scoring

CRITERIA = ["market_attractiveness", "technical_feasibility", "strategic_fit", "time_to_value", "risk"]
VALUES = {"A": [5, 4, 5, 3, 4], "B": [4, 5, 3, 5, 4], "C": [5, 3, 4, 2, 1], "D": [2, 3, 2, 4, 3], "E": [3, 2, 2, 2, 2]}
CONFIG = {
    "weights": dict(zip(CRITERIA, [0.25, 0.25, 0.20, 0.15, 0.15])),
    "sensitivity_runs": 1000,
    "random_seed": 42,
    "weight_variation": 0.5,
    "rules": {
        "top_n": 3,
        "pursue_top_share": 0.70,
        "pursue_min_total": 3.5,
        "park_top_share": 0.20,
        "park_max_total": 2.5,
        "near_tie": 0.25,
    },
    "time_criterion": "time_to_value",
    "months_to_value": {5: 3, 4: 9, 3: 18, 2: 30, 1: 42},
    "breakeven_years": 3,
}
WEIGHTS = CONFIG["weights"]


def opportunities() -> pd.DataFrame:
    rows = [(key, f"Example {key}", "example", "internal", "made up") for key in VALUES]
    return pd.DataFrame(rows, columns=scoring.OPPORTUNITY_COLUMNS)


def scores(assumptions: tuple = ()) -> pd.DataFrame:
    rows = []
    for key, values in VALUES.items():
        for criterion, value in zip(CRITERIA, values):
            evidence = "assumption: made up" if (key, criterion) in assumptions else "example value"
            rows.append((key, criterion, value, "made-up score", evidence))
    return pd.DataFrame(rows, columns=scoring.SCORE_COLUMNS)


def ranking(**changes) -> pd.DataFrame:
    return scoring.build_ranking(opportunities(), scores(), dict(CONFIG, **changes)).set_index("id")


# --- checking the inputs ----------------------------------------------------


def test_good_inputs_pass_the_check():
    scoring.check_inputs(opportunities(), scores(), WEIGHTS)


def test_weights_that_do_not_sum_to_one_are_rejected():
    with pytest.raises(ValueError, match="sum to 1"):
        scoring.check_weights(dict(WEIGHTS, risk=0.25))


def test_a_score_without_justification_is_rejected_and_named():
    broken = scores()
    broken.loc[0, "justification"] = " "
    with pytest.raises(ValueError, match="'A' for 'market_attractiveness' has no justification"):
        scoring.check_inputs(opportunities(), broken, WEIGHTS)


def test_a_score_without_evidence_is_rejected():
    broken = scores()
    broken.loc[3, "evidence"] = None
    with pytest.raises(ValueError, match="has no evidence"):
        scoring.check_inputs(opportunities(), broken, WEIGHTS)


@pytest.mark.parametrize("bad_score", [0, 6, 2.5])
def test_a_score_outside_1_to_5_is_rejected(bad_score):
    broken = scores().astype({"score": float})
    broken.loc[0, "score"] = bad_score
    with pytest.raises(ValueError, match="whole number from 1 to 5"):
        scoring.check_inputs(opportunities(), broken, WEIGHTS)


def test_a_missing_score_is_rejected():
    with pytest.raises(ValueError, match="exactly one score for 'market_attractiveness', found 0"):
        scoring.check_inputs(opportunities(), scores().iloc[1:], WEIGHTS)


def test_a_duplicated_score_is_rejected():
    doubled = pd.concat([scores(), scores().iloc[:1]], ignore_index=True)
    with pytest.raises(ValueError, match="found 2"):
        scoring.check_inputs(opportunities(), doubled, WEIGHTS)


def test_a_score_for_an_unknown_opportunity_or_criterion_is_rejected():
    unknown = scores()
    unknown.loc[0, "opportunity_id"] = "Z"
    with pytest.raises(ValueError, match="unknown opportunities"):
        scoring.check_inputs(opportunities(), unknown, WEIGHTS)
    unknown = scores()
    unknown.loc[0, "criterion"] = "beauty"
    with pytest.raises(ValueError, match="no weight"):
        scoring.check_inputs(opportunities(), unknown, WEIGHTS)


# --- the weighted score -----------------------------------------------------


def test_totals_match_the_hand_calculation():
    totals = scoring.weighted_totals(scoring.score_table(scores(), WEIGHTS), WEIGHTS)
    assert totals["A"] == pytest.approx(4.30)
    assert totals["C"] == pytest.approx(3.25)
    assert totals["E"] == pytest.approx(2.25)


def test_totals_do_not_depend_on_the_order_of_rows_in_the_file():
    shuffled = scores().sample(frac=1, random_state=1)
    totals = scoring.weighted_totals(scoring.score_table(shuffled, WEIGHTS), WEIGHTS)
    assert totals["B"] == pytest.approx(4.20)


def test_ranking_is_from_the_highest_total_down():
    assert list(ranking().index) == ["A", "B", "C", "D", "E"]
    assert list(ranking()["rank"]) == [1, 2, 3, 4, 5]


def test_near_ties_are_named():
    result = ranking()
    assert result.loc["A", "practically_tied"] == "B"   # 4.30 and 4.20
    assert result.loc["B", "practically_tied"] == "A"
    assert result.loc["C", "practically_tied"] == ""    # 0.95 below B


# --- sensitivity to the weights ---------------------------------------------


@pytest.mark.parametrize("variation", [0.5, None])
def test_every_random_set_of_weights_sums_to_one_and_has_no_negative_weight(variation):
    drawn = scoring.random_weights(WEIGHTS, 200, seed=1, variation=variation)
    assert drawn.shape == (200, 5)
    assert drawn.sum(axis=1) == pytest.approx(1.0)
    assert (drawn >= 0).all()


def test_the_same_seed_gives_the_same_draws_and_another_seed_different_ones():
    first = scoring.random_weights(WEIGHTS, 50, seed=7, variation=0.5)
    again = scoring.random_weights(WEIGHTS, 50, seed=7, variation=0.5)
    other = scoring.random_weights(WEIGHTS, 50, seed=8, variation=0.5)
    assert (first == again).all()
    assert not (first == other).all()


def test_top_shares_under_reasonable_disagreement():
    result = ranking()
    assert result.loc["A", "top_share"] == 1.0
    assert result.loc["B", "top_share"] == 1.0
    assert result.loc["C", "top_share"] > 0.9
    assert result.loc["D", "top_share"] < 0.1
    assert result.loc["E", "top_share"] == 0.0
    # In every run exactly three opportunities are in the top three.
    assert result["top_share"].sum() == pytest.approx(3.0)


def test_free_weights_show_that_third_place_depends_on_the_weights():
    result = ranking()
    assert result.loc["C", "top_share_free"] < result.loc["C", "top_share"]
    assert result.loc["D", "top_share_free"] > result.loc["D", "top_share"]


def test_first_place_is_shared_between_the_two_near_tied_opportunities():
    result = ranking()
    assert result.loc["A", "first_share"] + result.loc["B", "first_share"] == pytest.approx(1.0)
    assert 0.5 < result.loc["A", "first_share"] < 0.9


def test_swap_points_match_the_hand_calculation():
    swaps = scoring.swap_points(scoring.score_table(scores(), WEIGHTS), WEIGHTS).set_index("criterion")
    assert swaps.loc["market_attractiveness", "swap_weight"] == pytest.approx(0.16)
    assert swaps.loc["technical_feasibility", "swap_weight"] == pytest.approx(0.32)
    assert swaps.loc["strategic_fit", "swap_weight"] == pytest.approx(0.15)
    assert swaps.loc["time_to_value", "swap_weight"] == pytest.approx(0.20)
    # A and B both score 4 on risk, so no weight for risk can swap them.
    assert pd.isna(swaps.loc["risk", "swap_weight"])


# --- classification ---------------------------------------------------------


def test_classification_of_the_example():
    assert list(ranking()["classification"]) == ["pursue", "pursue", "explore", "park", "park"]


def test_a_score_of_one_blocks_pursue_even_with_a_high_total():
    name, reason = scoring.classify(total=4.4, top_share=1.0, has_score_of_one=True, rules=CONFIG["rules"])
    assert name == "explore"
    assert "knock-out" in reason


def test_a_stable_top_rank_is_not_enough_without_a_strong_total():
    # This is why "nothing qualifies for pursue" is a possible outcome.
    name, _ = scoring.classify(total=3.2, top_share=1.0, has_score_of_one=False, rules=CONFIG["rules"])
    assert name == "explore"


def test_park_by_rank_and_park_by_total():
    rules = CONFIG["rules"]
    assert scoring.classify(2.7, 0.02, False, rules) == ("park", "rarely in the top group")
    assert scoring.classify(2.4, 0.50, False, rules) == ("park", "total below the minimum")


def test_score_without_time_matches_the_hand_calculation():
    # A without time: (1.25 + 1.00 + 1.00 + 0.60) / 0.85 = 4.529
    result = ranking()
    assert result.loc["A", "score_without_time"] == pytest.approx(4.529, abs=1e-3)
    assert result.loc["A", "months_to_value"] == 18   # time score 3
    assert result.loc["B", "months_to_value"] == 3    # time score 5


# --- sensitivity to uncertain scores ----------------------------------------


def test_only_scores_resting_on_an_assumption_are_varied():
    assumptions = (("A", "market_attractiveness"), ("C", "risk"))
    test = scoring.uncertain_score_test(opportunities(), scores(assumptions), CONFIG)
    # A's 5 cannot go up, C's 1 cannot go down: two rows remain.
    assert [(row.opportunity_id, row.direction) for row in test.itertuples()] == [("A", "down"), ("C", "up")]


def test_uncertain_score_results_match_the_hand_calculation():
    assumptions = (("A", "market_attractiveness"), ("C", "risk"))
    test = scoring.uncertain_score_test(opportunities(), scores(assumptions), CONFIG).set_index("opportunity_id")
    # A's market score 5 -> 4: total 4.05, now below B. Order changes, group does not.
    assert test.loc["A", "new_total"] == pytest.approx(4.05)
    assert test.loc["A", "top_order_changed"] and not test.loc["A", "top_group_changed"]
    # C's risk score 1 -> 2: total 3.40. No knock-out any more, but still under 3.5.
    assert test.loc["C", "new_total"] == pytest.approx(3.40)
    assert test.loc["C", "classification_changes"] == ""


def test_no_assumptions_gives_an_empty_table():
    assert len(scoring.uncertain_score_test(opportunities(), scores(), CONFIG)) == 0


# --- the cost-benefit view --------------------------------------------------


def business_case() -> pd.DataFrame:
    rows = [
        ("A", "investment", "One-off investment", 300_000, 400_000, 500_000, "EUR", None, "assumption"),
        ("A", "running_cost", "Yearly running cost", 60_000, 60_000, 60_000, "EUR", None, "assumption"),
        ("A", "benefit", "Downtime hours avoided", 400, 600, 800, "hours", 500, "assumption"),
    ]
    return pd.DataFrame(rows, columns=scoring.BUSINESS_CASE_COLUMNS)


def test_payback_in_three_cases_matches_the_hand_calculation():
    results = scoring.business_case_results(business_case(), 3).set_index("case")
    assert results.loc["cautious", "payback_years"] == pytest.approx(500 / 140, abs=1e-3)    # 3.57
    assert results.loc["base", "payback_years"] == pytest.approx(400 / 240, abs=1e-3)        # 1.67
    assert results.loc["optimistic", "payback_years"] == pytest.approx(300 / 340, abs=1e-3)  # 0.88


def test_break_even_quantity_matches_the_hand_calculation():
    # Needed: 400,000 / 3 + 60,000 = 193,333 a year; at 500 an hour that is 387 hours.
    results = scoring.business_case_results(business_case(), 3)
    breakeven = results[results["breakeven_quantity"].notna()].iloc[0]
    assert breakeven["breakeven_quantity"] == pytest.approx(386.67, abs=0.01)
    assert breakeven["base_quantity"] == 600


def test_no_payback_when_the_benefit_does_not_cover_the_running_cost():
    assert pd.isna(scoring.payback_years(400_000, yearly_benefit=50_000, yearly_running_cost=60_000))
    assert pd.isna(scoring.payback_years(400_000, yearly_benefit=60_000, yearly_running_cost=60_000))


def test_a_business_case_row_without_a_source_is_rejected():
    broken = business_case()
    broken.loc[0, "source"] = ""
    with pytest.raises(ValueError, match="has no source"):
        scoring.check_business_case(broken, opportunities())


def test_a_business_case_row_with_low_above_high_is_rejected():
    broken = business_case()
    broken.loc[0, "low"] = 600_000
    with pytest.raises(ValueError, match="low <= base <= high"):
        scoring.check_business_case(broken, opportunities())
