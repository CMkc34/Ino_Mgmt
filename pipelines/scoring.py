"""The opportunity scoring model (deliverable D3).

Method: docs/design/scoring-model-method.md. In short:

  1. Each opportunity gets a score from 1 to 5 on each criterion.
  2. The total is the weighted sum of its scores.
  3. Sensitivity tests show how far the ranking depends on the weights and
     on scores that rest on assumptions.
  4. A rule, fixed in advance, sorts each opportunity into pursue, explore
     or park.

Like transform.py, the functions here take tables and numbers in and give
tables and numbers out. Only `load_inputs` reads files.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from pipelines.io import read_csv

OPPORTUNITY_COLUMNS = ["id", "name", "subtopic_id", "use", "description"]
SCORE_COLUMNS = ["opportunity_id", "criterion", "score", "justification", "evidence"]
BUSINESS_CASE_COLUMNS = ["opportunity_id", "kind", "item", "low", "base", "high", "unit", "unit_value", "source"]
BUSINESS_CASE_KINDS = ["investment", "running_cost", "benefit"]


# --- reading and checking the inputs ------------------------------------------


def check_weights(weights: dict) -> None:
    """Stop if the weights do not sum to 1 (acceptance criterion AC-3.5).

    Compared with a small tolerance: 0.25 + 0.25 + 0.20 + 0.15 + 0.15 is not
    exactly 1 in a computer's arithmetic.
    """
    total = sum(weights.values())
    if abs(total - 1) > 1e-9:
        raise ValueError(f"the weights must sum to 1, but they sum to {total:.4f}")
    if any(weight < 0 for weight in weights.values()):
        raise ValueError("a weight must not be negative")


def check_inputs(opportunities: pd.DataFrame, scores: pd.DataFrame, weights: dict) -> None:
    """Stop with a message that names the problem if the input is not usable.

    Checks, in this order: the weights; the columns; that every score
    belongs to a known opportunity and a known criterion; that every
    opportunity has exactly one score per criterion; that every score is a
    whole number from 1 to 5; and that every score has a justification and
    evidence (acceptance criterion AC-3.4).
    """
    check_weights(weights)
    for name, table, columns in (
        ("opportunities.csv", opportunities, OPPORTUNITY_COLUMNS),
        ("scores.csv", scores, SCORE_COLUMNS),
    ):
        missing = set(columns) - set(table.columns)
        if missing:
            raise ValueError(f"{name} is missing columns: {sorted(missing)}")

    if opportunities["id"].duplicated().any():
        raise ValueError("opportunities.csv lists an id twice")

    unknown = sorted(set(scores["opportunity_id"]) - set(opportunities["id"]))
    if unknown:
        raise ValueError(f"scores.csv has scores for unknown opportunities: {unknown}")
    unknown = sorted(set(scores["criterion"]) - set(weights))
    if unknown:
        raise ValueError(f"scores.csv uses criteria that have no weight: {unknown}")

    for opportunity_id in opportunities["id"]:
        own = scores[scores["opportunity_id"] == opportunity_id]
        for criterion in weights:
            count = int((own["criterion"] == criterion).sum())
            if count != 1:
                raise ValueError(
                    f"opportunity '{opportunity_id}' needs exactly one score for '{criterion}', found {count}"
                )

    for row in scores.itertuples():
        where = f"score of '{row.opportunity_id}' for '{row.criterion}'"
        if row.score not in (1, 2, 3, 4, 5):
            raise ValueError(f"the {where} must be a whole number from 1 to 5, not {row.score}")
        for field in ("justification", "evidence"):
            value = getattr(row, field)
            if pd.isna(value) or not str(value).strip():
                raise ValueError(f"the {where} has no {field}")


def load_inputs(input_dir: Path, weights: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None]:
    """Read and check the opportunity list, the scores and (if present) the business case."""
    opportunities = read_csv(input_dir / "opportunities.csv")
    scores = read_csv(input_dir / "scores.csv")
    check_inputs(opportunities, scores, weights)

    business_case = None
    path = input_dir / "business-case.csv"
    if path.exists():
        business_case = read_csv(path)
        check_business_case(business_case, opportunities)
    return opportunities, scores, business_case


# --- the weighted score ---------------------------------------------------------


def score_table(scores: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """Reshape the scores: one row per opportunity, one column per criterion.

    The columns are put in the order of the weights by NAME. Relying on the
    order in the file would give wrong totals without any error if the two
    orders ever differed.
    """
    table = scores.pivot(index="opportunity_id", columns="criterion", values="score")
    return table[list(weights)].sort_index()


def weighted_totals(table: pd.DataFrame, weights: dict) -> pd.Series:
    """Total score per opportunity: the sum of score x weight over all criteria."""
    weight_row = pd.Series(weights)
    return (table[list(weights)] * weight_row).sum(axis=1)


def ranked(totals: pd.Series) -> list[str]:
    """Opportunity ids from the highest total to the lowest.

    Equal totals are ordered by id, so the ranking is always the same.
    """
    frame = pd.DataFrame({"total": totals, "id": totals.index})
    return list(frame.sort_values(["total", "id"], ascending=[False, True])["id"])


# --- sensitivity to the weights ---------------------------------------------------


def random_weights(weights: dict, runs: int, seed: int, variation: float | None) -> np.ndarray:
    """Draw `runs` alternative sets of weights. Each set sums to 1.

    variation = 0.5   "reasonable disagreement": every weight is multiplied
                      by its own random factor between 0.5 and 1.5, then all
                      are rescaled to sum to 1.
    variation = None  "free weights": any combination that sums to 1, all
                      equally likely.

    The fixed seed makes the draws identical on every run.
    """
    generator = np.random.default_rng(seed)
    base = np.array(list(weights.values()), dtype=float)
    if variation is None:
        return generator.dirichlet(np.ones(len(base)), size=runs)
    drawn = base * generator.uniform(1 - variation, 1 + variation, size=(runs, len(base)))
    return drawn / drawn.sum(axis=1, keepdims=True)


def top_shares(table: pd.DataFrame, weight_sets: np.ndarray, top_n: int) -> tuple[pd.Series, pd.Series]:
    """In what share of the runs is each opportunity in the top `top_n`, and ranked first?

    Returns two columns indexed by opportunity id: the top-n share and the
    share of runs in which the opportunity is ranked first.
    """
    values = table.to_numpy(dtype=float)       # opportunities x criteria
    totals = weight_sets @ values.T            # runs x opportunities
    # A stable sort keeps the order of the table (sorted by id) for equal totals.
    order = np.argsort(-totals, axis=1, kind="stable")
    in_top = np.zeros(totals.shape, dtype=bool)
    np.put_along_axis(in_top, order[:, :top_n], True, axis=1)
    is_first = np.zeros(totals.shape, dtype=bool)
    np.put_along_axis(is_first, order[:, :1], True, axis=1)
    return (
        pd.Series(in_top.mean(axis=0), index=table.index),
        pd.Series(is_first.mean(axis=0), index=table.index),
    )


def swap_points(table: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """For each criterion: at which weight do ranks 1 and 2 swap? (method note, 7.3)

    One weight is tried at every value from 0.00 to 1.00. The other weights
    keep their proportions and are rescaled so that all still sum to 1.
    Reported is the swapping weight closest to the base weight, or an empty
    cell if ranks 1 and 2 never swap for that criterion.
    """
    first, second = ranked(weighted_totals(table, weights))[:2]
    rows = []
    for criterion, base_weight in weights.items():
        swaps = []
        for step in range(101):
            trial = step / 100
            scale = (1 - trial) / (1 - base_weight)
            trial_weights = {name: weight * scale for name, weight in weights.items()}
            trial_weights[criterion] = trial
            totals = weighted_totals(table, trial_weights)
            if totals[second] > totals[first]:
                swaps.append(trial)
        nearest = min(swaps, key=lambda value: abs(value - base_weight)) if swaps else float("nan")
        rows.append(
            {
                "criterion": criterion,
                "base_weight": base_weight,
                "swap_weight": nearest,
                "change_needed": abs(nearest - base_weight) if swaps else float("nan"),
                "rank_1": first,
                "rank_2": second,
            }
        )
    return pd.DataFrame(rows)


# --- classification -----------------------------------------------------------------


def classify(total: float, top_share: float, has_score_of_one: bool, rules: dict) -> tuple[str, str]:
    """Sort one opportunity into pursue, explore or park, and say why (method note, 8).

    pursue   in the top group in enough runs, AND a high enough total, AND no
             score of 1 (the knock-out rule)
    park     rarely in the top group, OR a low total
    explore  everything else
    """
    stable = top_share >= rules["pursue_top_share"]
    strong = total >= rules["pursue_min_total"]
    if stable and strong and not has_score_of_one:
        return "pursue", "stable in the top group, strong total, no score of 1"
    if top_share < rules["park_top_share"]:
        return "park", "rarely in the top group"
    if total < rules["park_max_total"]:
        return "park", "total below the minimum"

    reasons = []
    if not stable:
        reasons.append("not stable in the top group")
    if not strong:
        reasons.append("total below the bar for pursue")
    if has_score_of_one:
        reasons.append("has a score of 1 (knock-out rule)")
    return "explore", "; ".join(reasons)


def near_tie_partners(totals: pd.Series, near_tie: float) -> pd.Series:
    """For each opportunity: the ids whose total is within `near_tie` of its own."""
    partners = {}
    for opportunity_id, total in totals.items():
        close = [
            other
            for other, other_total in totals.items()
            if other != opportunity_id and abs(other_total - total) < near_tie - 1e-9
        ]
        partners[opportunity_id] = " ".join(sorted(close))
    return pd.Series(partners)


def build_ranking(opportunities: pd.DataFrame, scores: pd.DataFrame, scoring_config: dict) -> pd.DataFrame:
    """The full result table of the scoring model, best total first.

    Columns: id, name, subtopic_id, use, one column per criterion, then
        total               weighted sum of the scores
        rank                1 = highest total
        practically_tied    ids whose total is closer than `near_tie`
        top_share           share of runs in the top group, weights varied
                            by `weight_variation` ("reasonable disagreement")
        first_share         share of those runs in which it is ranked first
        top_share_free      the same top share with freely drawn weights
        has_score_of_one    True if any criterion is scored 1
        classification      pursue, explore or park
        reason              why
        months_to_value     midpoint of the time band of its time score
        score_without_time  total over the other criteria, rescaled; the
                            vertical position in the time-horizon chart
    """
    weights = scoring_config["weights"]
    rules = scoring_config["rules"]
    table = score_table(scores, weights)
    totals = weighted_totals(table, weights)

    runs, seed = scoring_config["sensitivity_runs"], scoring_config["random_seed"]
    narrow = random_weights(weights, runs, seed, scoring_config["weight_variation"])
    free = random_weights(weights, runs, seed + 1, None)
    top_share, first_share = top_shares(table, narrow, rules["top_n"])
    top_share_free, _ = top_shares(table, free, rules["top_n"])

    result = table.copy()
    result["total"] = totals
    result["practically_tied"] = near_tie_partners(totals, rules["near_tie"])
    result["top_share"] = top_share
    result["first_share"] = first_share
    result["top_share_free"] = top_share_free
    result["has_score_of_one"] = (table == 1).any(axis=1)
    classes = [
        classify(result.loc[i, "total"], result.loc[i, "top_share"], bool(result.loc[i, "has_score_of_one"]), rules)
        for i in result.index
    ]
    result["classification"] = [name for name, _ in classes]
    result["reason"] = [reason for _, reason in classes]

    time_criterion = scoring_config["time_criterion"]
    months = {int(score): value for score, value in scoring_config["months_to_value"].items()}
    result["months_to_value"] = table[time_criterion].map(months)
    other = {name: weight for name, weight in weights.items() if name != time_criterion}
    rescaled = {name: weight / sum(other.values()) for name, weight in other.items()}
    result["score_without_time"] = weighted_totals(table, rescaled)

    order = ranked(totals)
    result = result.loc[order]
    result.insert(len(weights) + 1, "rank", range(1, len(result) + 1))
    details = opportunities.set_index("id")[["name", "subtopic_id", "use"]]
    return details.join(result, how="right").loc[order].rename_axis("id").reset_index()


# --- sensitivity to uncertain scores -----------------------------------------------


def uncertain_score_test(opportunities: pd.DataFrame, scores: pd.DataFrame, scoring_config: dict) -> pd.DataFrame:
    """Move each score that rests on an assumption by one point, up and down (method note, 7.4).

    A score counts as uncertain if its evidence starts with the word
    "assumption". For each such score and each direction, the model is
    recomputed with only that one score changed. Reported is what changed:
    the top group, the ranking of the top group, any classification.
    """
    base = build_ranking(opportunities, scores, scoring_config).set_index("id")
    top_n = scoring_config["rules"]["top_n"]
    base_top = list(base.index[:top_n])

    rows = []
    uncertain = scores[scores["evidence"].astype(str).str.strip().str.lower().str.startswith("assumption")]
    for row in uncertain.itertuples():
        for step, direction in ((1, "up"), (-1, "down")):
            new_score = row.score + step
            if not 1 <= new_score <= 5:
                continue
            changed = scores.copy()
            changed.loc[row.Index, "score"] = new_score
            result = build_ranking(opportunities, changed, scoring_config).set_index("id")
            new_top = list(result.index[:top_n])
            changed_classes = [
                f"{i}: {base.loc[i, 'classification']} to {result.loc[i, 'classification']}"
                for i in base.index
                if base.loc[i, "classification"] != result.loc[i, "classification"]
            ]
            rows.append(
                {
                    "opportunity_id": row.opportunity_id,
                    "criterion": row.criterion,
                    "direction": direction,
                    "score_from": row.score,
                    "score_to": new_score,
                    "new_total": result.loc[row.opportunity_id, "total"],
                    "top_group_changed": set(new_top) != set(base_top),
                    "top_order_changed": new_top != base_top,
                    "classification_changes": "; ".join(changed_classes),
                }
            )
    columns = [
        "opportunity_id", "criterion", "direction", "score_from", "score_to", "new_total",
        "top_group_changed", "top_order_changed", "classification_changes",
    ]
    return pd.DataFrame(rows, columns=columns)


# --- the cost-benefit view ------------------------------------------------------------


def check_business_case(business_case: pd.DataFrame, opportunities: pd.DataFrame) -> None:
    """Stop if the business case input is not usable.

    Every row needs a source or the word "assumption" (acceptance criterion
    AC-3.10), and low <= base <= high.
    """
    missing = set(BUSINESS_CASE_COLUMNS) - set(business_case.columns)
    if missing:
        raise ValueError(f"business-case.csv is missing columns: {sorted(missing)}")
    unknown = sorted(set(business_case["opportunity_id"]) - set(opportunities["id"]))
    if unknown:
        raise ValueError(f"business-case.csv has rows for unknown opportunities: {unknown}")
    for row in business_case.itertuples():
        where = f"business case row '{row.item}' of '{row.opportunity_id}'"
        if row.kind not in BUSINESS_CASE_KINDS:
            raise ValueError(f"the {where} has the kind '{row.kind}'; allowed: {BUSINESS_CASE_KINDS}")
        if not row.low <= row.base <= row.high:
            raise ValueError(f"the {where} needs low <= base <= high")
        if pd.isna(row.source) or not str(row.source).strip():
            raise ValueError(f'the {where} has no source (write "assumption" if it is one)')
        if row.kind == "benefit" and (pd.isna(row.unit_value) or row.unit_value <= 0):
            raise ValueError(f"the {where} is a benefit and needs a unit_value above 0")


def payback_years(investment: float, yearly_benefit: float, yearly_running_cost: float) -> float:
    """Years until the yearly net benefit has paid back the one-off investment.

    Simple payback, without discounting. Returns an empty value ("no
    payback") if the yearly net benefit is zero or negative.
    """
    net = yearly_benefit - yearly_running_cost
    if net <= 0:
        return float("nan")
    return investment / net


def business_case_results(business_case: pd.DataFrame, breakeven_years: float) -> pd.DataFrame:
    """Payback in three cases, and the break-even view, per opportunity (method note, 10).

    Input rows have a kind:
        investment     one-off cost; low / base / high in money
        running_cost   yearly cost;  low / base / high in money
        benefit        a benefit DRIVER: low / base / high is a quantity per
                       year (e.g. downtime hours avoided) and unit_value is
                       what one unit is worth. Yearly benefit = quantity x
                       unit_value. Several drivers are added up.

    Cases: cautious = high costs with low benefits; base; optimistic = low
    costs with high benefits.

    Break-even: how large must the FIRST benefit driver be for payback
    within `breakeven_years` at base costs, with any other drivers at base?
    """
    rows = []
    for opportunity_id, own in business_case.groupby("opportunity_id", sort=True):
        investment = own[own["kind"] == "investment"]
        running = own[own["kind"] == "running_cost"]
        benefits = own[own["kind"] == "benefit"]
        if len(benefits) == 0 or len(investment) == 0:
            raise ValueError(f"the business case of '{opportunity_id}' needs an investment and a benefit row")

        def benefit_sum(column: str) -> float:
            return float((benefits[column] * benefits["unit_value"]).sum())

        cases = {
            "cautious": (investment["high"].sum(), benefit_sum("low"), running["high"].sum()),
            "base": (investment["base"].sum(), benefit_sum("base"), running["base"].sum()),
            "optimistic": (investment["low"].sum(), benefit_sum("high"), running["low"].sum()),
        }
        for case, (invest, benefit, cost) in cases.items():
            rows.append(
                {
                    "opportunity_id": opportunity_id,
                    "case": case,
                    "investment": float(invest),
                    "yearly_benefit": benefit,
                    "yearly_running_cost": float(cost),
                    "yearly_net_benefit": benefit - float(cost),
                    "payback_years": payback_years(float(invest), benefit, float(cost)),
                }
            )

        main = benefits.iloc[0]
        base_invest, base_benefit, base_cost = cases["base"]
        other_benefit = base_benefit - main["base"] * main["unit_value"]
        needed_benefit = base_invest / breakeven_years + base_cost - other_benefit
        rows.append(
            {
                "opportunity_id": opportunity_id,
                "case": f"break-even for payback in {breakeven_years:g} years",
                "investment": float(base_invest),
                "yearly_benefit": float(base_invest / breakeven_years + base_cost),
                "yearly_running_cost": float(base_cost),
                "yearly_net_benefit": float(base_invest / breakeven_years),
                "payback_years": float(breakeven_years),
                "breakeven_driver": main["item"],
                "breakeven_quantity": float(needed_benefit / main["unit_value"]),
                "breakeven_unit": main["unit"],
                "base_quantity": float(main["base"]),
            }
        )
    columns = [
        "opportunity_id", "case", "investment", "yearly_benefit", "yearly_running_cost", "yearly_net_benefit",
        "payback_years", "breakeven_driver", "breakeven_quantity", "breakeven_unit", "base_quantity",
    ]
    return pd.DataFrame(rows, columns=columns)
