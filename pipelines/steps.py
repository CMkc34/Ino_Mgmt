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
from pipelines.paths import FIGURES_DIR, MANUAL_DIR, PROCESSED_DIR, RAW_DIR, in_repo


def run_trend_scan(config: dict, refresh: bool, config_key: str, folder: str) -> str:
    """One trend scan: snapshot -> metrics -> charts.

    config_key   the section of config.yaml that defines the scan
    folder       "" for the first scan; otherwise the sub-folder that holds
                 this scan's files inside data/raw, data/manual,
                 data/processed and outputs/figures, so that two scans never
                 mix their files
    """
    trends_config = config[config_key]
    raw_dir, manual_dir = RAW_DIR / folder, MANUAL_DIR / folder
    processed_dir, figures_dir = PROCESSED_DIR / folder, FIGURES_DIR / folder

    if refresh:
        today = dt.date.today()
        # The main counts and the robustness variants, each in its own file.
        for variant, prefix in ingest.VARIANTS.items():
            counts = ingest.fetch_publication_counts(trends_config, variant=variant)
            snapshot = ingest.save_snapshot(counts, fetch_date=today, raw_dir=raw_dir, prefix=prefix)
            ingest.save_snapshot_note(snapshot, trends_config, fetch_date=today, variant=variant)
            print(f"  new snapshot written: {snapshot.name}")
        topics = ingest.fetch_discovery_topics(trends_config)
        snapshot = ingest.save_discovery_topics(topics, fetch_date=today, raw_dir=raw_dir)
        print(f"  new snapshot written: {snapshot.name}")

    snapshot = ingest.find_latest_snapshot(raw_dir)
    if snapshot is None:
        return "skipped (no snapshot yet; run with --refresh to fetch one)"

    counts = ingest.load_snapshot(snapshot)
    fetch_date = snapshot.stem.removeprefix(ingest.SNAPSHOT_PREFIX)  # the date in the file name

    # The robustness data sets, where a snapshot of them exists.
    variant_counts = {}
    for variant, prefix in ingest.VARIANTS.items():
        if variant == "main":
            continue
        variant_snapshot = ingest.find_latest_snapshot(raw_dir, prefix=prefix)
        if variant_snapshot is not None:
            variant_counts[variant] = ingest.load_snapshot(variant_snapshot)

    results = transform.build_trend_results(
        counts,
        trends_config,
        quality=ingest.load_query_quality(manual_dir),
        variant_counts=variant_counts,
        adoption=ingest.load_adoption(manual_dir),
    )
    write_csv(results, processed_dir / "trend_metrics.csv")
    # The yearly counts as one table (one row per sub-topic, one column per
    # year), so every count quoted in the write-up can be looked up here.
    yearly = transform.yearly_table(counts).rename(columns=str).reset_index()
    write_csv(yearly, processed_dir / "trend_counts_by_year.csv")

    save_figure(figures.plot_time_series(counts, results, trends_config, fetch_date), "trend_time_series", figures_dir)
    save_figure(figures.plot_trend_map(results, trends_config, fetch_date), "trend_map", figures_dir)

    # Discovery step: which of the source's own topic labels grew fastest?
    discovery_note = ""
    discovery_snapshot = ingest.find_latest_snapshot(raw_dir, prefix=ingest.DISCOVERY_PREFIX)
    if discovery_snapshot is not None:
        field = transform.yearly_table(counts).loc[transform.FIELD_ID]
        last_year = trends_config["last_year"]
        steps = trends_config["growth_window_years"]
        field_momentum = transform.compound_annual_growth_rate(field[last_year - steps], field[last_year], steps)
        ranking = transform.discovery_ranking(
            ingest.load_discovery_topics(discovery_snapshot),
            field_momentum,
            trends_config,
            mapping=ingest.load_discovery_mapping(manual_dir),
        )
        write_csv(ranking, processed_dir / "discovery_top_topics.csv")
        discovery_note = ", discovery_top_topics.csv"

    shortlisted = int(results["on_shortlist_by_rule"].sum())
    return (
        f"snapshot {snapshot.name}: {len(results)} sub-topics, "
        f"{int(results['emerging'].sum())} emerging, {shortlisted} on the shortlist by rule; "
        f"wrote trend_metrics.csv{discovery_note} and 2 charts"
    )


def run_trends(config: dict, refresh: bool = False) -> str:
    """The first trend scan: AI in industrial manufacturing (deliverable D2)."""
    return run_trend_scan(config, refresh, config_key="trends", folder="")


def run_trends_medtech(config: dict, refresh: bool = False) -> str:
    """The second trend scan: AI in medical technology (deliverable D10)."""
    return run_trend_scan(config, refresh, config_key="trends_medtech", folder="medtech")


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
    "trends_medtech": run_trends_medtech,
    "scoring": run_scoring,
}
