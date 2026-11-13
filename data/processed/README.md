# Processed data

Analysis-ready CSV files written by the pipeline. Do not edit by hand: change the code or `config.yaml` and re-run.

## `discovery_top_topics.csv`

The discovery step: the 15 topic labels of the source that grew fastest within the field, among labels with at least 30 works in 2020. `closest_subtopic` says which of the ten sub-topics a label corresponds to; "none" marks a label the list does not cover. Labels are the source's own classification of each work, which is coarser than the sub-topics and has no label for some of them.

## `trend_metrics.csv`

One row per sub-topic, strongest growth relative to the field first, emerging sub-topics last. Definitions are in the [trend scan method](../../docs/design/trend-scan-method.md).

| Column | Meaning |
|---|---|
| `works_start`, `works_end` | Works in the first and last year of the growth window (2020 and 2025) |
| `volume` | Works in the last three years |
| `share` | Volume divided by the field's volume |
| `emerging` | True if `works_start` is under the threshold (30); then no growth rate is computed |
| `momentum` | Compound annual growth rate over the window (0.35 means 35% a year) |
| `relative_momentum` | Momentum minus the field's momentum. Above 0: outgrows the field |
| `relative_momentum_shifted` | Robustness test A: window 2019 to 2024 |
| `relative_momentum_smoothed` | Robustness test B: start and end are two-year averages |
| `robustness` | `robust` (same side of the field in the main result and tests A and B), `not robust`, `not testable` (a test has no rate because its start value is under the threshold) or `emerging` |
| `relative_momentum_no_ai` | Robustness test D: the same calculation without any AI condition in the search |
| `relative_momentum_articles` | Robustness test C: works of type "article" only |
| `quality_share` | Share of relevant works in the query-quality check (lowest rater, last round) |
| `passes_quality` | `quality_share` reaches the threshold (0.70) |
| `rising_three_years` | The yearly count rose in each of the last three years |
| `on_shortlist_by_rule` | Rules 1 to 3 of the shortlist rule. Rules 4 and 5 need judgement and are applied in the write-up |
| `adoption_level` | From `data/manual/adoption.csv`; empty until that file is filled in |

## Scoring model

Written by `python -m pipelines run scoring` from the input set named in `config.yaml` (`scoring.input_dir`). Definitions are in the [scoring model method](../../docs/design/scoring-model-method.md). **At present the input is the made-up example set, so these files show how the model works and are not findings.**

| File | Content |
|---|---|
| `scoring_ranking.csv` | One row per opportunity, best total first: the scores, `total`, `rank`, `practically_tied` (totals closer than 0.25), `top_share` (share of runs in the top three, weights varied by up to 50%), `first_share`, `top_share_free` (the same with freely drawn weights), `has_score_of_one`, `classification` (pursue, explore, park) with its `reason`, `months_to_value` and `score_without_time` |
| `scoring_swap_points.csv` | For each criterion: the weight at which ranks 1 and 2 would swap, or empty if they never do |
| `scoring_uncertain_scores.csv` | Each score that rests on an assumption, moved one point up and down: the new total and what changed in the top group and the classification |
| `scoring_business_case.csv` | Payback in a cautious, a base and an optimistic case, and the break-even row: how large the main benefit driver must be for payback within three years |
