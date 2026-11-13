"""The pipeline steps and the order they run in.

Each step is a function that takes the configuration and returns a short
status message. A step that has no input data yet reports that it was
skipped, so `run all` still finishes cleanly while the project is being
built.
"""

import datetime as dt

from pipelines import figures, ingest, scoring, transform
from pipelines.figures import save_figure
from pipelines.io import write_csv
from pipelines.paths import PROCESSED_DIR, in_repo


def run_trends(config: dict, refresh: bool = False) -> str:
    """Trend scan data: snapshot -> metrics -> charts (deliverable D2)."""
    trends_config = config["trends"]

    if refresh:
        today = dt.date.today()
        # The main counts and the robustness variants, each in its own file.
        for variant, prefix in ingest.VARIANTS.items():
            counts = ingest.fetch_publication_counts(trends_config, variant=variant)
            snapshot = ingest.save_snapshot(counts, fetch_date=today, prefix=prefix)
            ingest.save_snapshot_note(snapshot, trends_config, fetch_date=today, variant=variant)
            print(f"  new snapshot written: {snapshot.name}")
        topics = ingest.fetch_discovery_topics(trends_config)
        snapshot = ingest.save_discovery_topics(topics, fetch_date=today)
        print(f"  new snapshot written: {snapshot.name}")

    snapshot = ingest.find_latest_snapshot()
    if snapshot is None:
        return "skipped (no snapshot in data/raw/ yet; run with --refresh to fetch one)"

    counts = ingest.load_snapshot(snapshot)
    fetch_date = snapshot.stem.removeprefix(ingest.SNAPSHOT_PREFIX)  # the date in the file name

    # The robustness data sets, where a snapshot of them exists.
    variant_counts = {}
    for variant, prefix in ingest.VARIANTS.items():
        if variant == "main":
            continue
        variant_snapshot = ingest.find_latest_snapshot(prefix=prefix)
        if variant_snapshot is not None:
            variant_counts[variant] = ingest.load_snapshot(variant_snapshot)

    results = transform.build_trend_results(
        counts,
        trends_config,
        quality=ingest.load_query_quality(),
        variant_counts=variant_counts,
        adoption=ingest.load_adoption(),
    )
    write_csv(results, PROCESSED_DIR / "trend_metrics.csv")
    # The yearly counts as one table (one row per sub-topic, one column per
    # year), so every count quoted in the write-up can be looked up here.
    yearly = transform.yearly_table(counts).rename(columns=str).reset_index()
    write_csv(yearly, PROCESSED_DIR / "trend_counts_by_year.csv")

    save_figure(figures.plot_time_series(counts, results, trends_config, fetch_date), "trend_time_series")
    save_figure(figures.plot_trend_map(results, trends_config, fetch_date), "trend_map")

    # Discovery step: which of the source's own topic labels grew fastest?
    discovery_note = ""
    discovery_snapshot = ingest.find_latest_snapshot(prefix=ingest.DISCOVERY_PREFIX)
    if discovery_snapshot is not None:
        field = transform.yearly_table(counts).loc[transform.FIELD_ID]
        last_year = trends_config["last_year"]
        steps = trends_config["growth_window_years"]
        field_momentum = transform.compound_annual_growth_rate(field[last_year - steps], field[last_year], steps)
        ranking = transform.discovery_ranking(
            ingest.load_discovery_topics(discovery_snapshot),
            field_momentum,
            trends_config,
            mapping=ingest.load_discovery_mapping(),
        )
        write_csv(ranking, PROCESSED_DIR / "discovery_top_topics.csv")
        discovery_note = ", discovery_top_topics.csv"

    shortlisted = int(results["on_shortlist_by_rule"].sum())
    return (
        f"snapshot {snapshot.name}: {len(results)} sub-topics, "
        f"{int(results['emerging'].sum())} emerging, {shortlisted} on the shortlist by rule; "
        f"wrote trend_metrics.csv{discovery_note} and 2 charts"
    )


def run_scoring(config: dict, refresh: bool = False) -> str:
    """Opportunity scoring: inputs -> ranking -> sensitivity tests -> charts (deliverable D3)."""
    scoring_config = config["scoring"]
    input_dir = in_repo(scoring_config["input_dir"])
    if not (input_dir / "scores.csv").exists():
        return f"skipped (no scores.csv in {scoring_config['input_dir']})"

    opportunities, scores, business_case = scoring.load_inputs(input_dir, scoring_config["weights"])

    ranking = scoring.build_ranking(opportunities, scores, scoring_config)
    write_csv(ranking, PROCESSED_DIR / "scoring_ranking.csv")

    table = scoring.score_table(scores, scoring_config["weights"])
    write_csv(scoring.swap_points(table, scoring_config["weights"]), PROCESSED_DIR / "scoring_swap_points.csv")
    write_csv(
        scoring.uncertain_score_test(opportunities, scores, scoring_config),
        PROCESSED_DIR / "scoring_uncertain_scores.csv",
    )
    if business_case is not None:
        write_csv(
            scoring.business_case_results(business_case, scoring_config["breakeven_years"]),
            PROCESSED_DIR / "scoring_business_case.csv",
        )

    save_figure(figures.plot_rank_stability(ranking, scoring_config), "scoring_rank_stability")
    save_figure(figures.plot_time_horizon(ranking, scoring_config), "scoring_time_horizon")

    classes = ranking["classification"].value_counts()
    summary = ", ".join(f"{classes.get(name, 0)} {name}" for name in ("pursue", "explore", "park"))
    return f"{len(ranking)} opportunities from {scoring_config['input_dir']}: {summary}; wrote 4 tables and 2 charts"


# Order matters: `run all` goes through this dictionary from top to bottom.
STEPS = {
    "trends": run_trends,
    "scoring": run_scoring,
}
