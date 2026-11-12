"""The pipeline steps and the order they run in.

Each step is a function that takes the configuration and returns a short
status message. A step that has no input data yet reports that it was
skipped, so `run all` still finishes cleanly while the project is being
built.
"""

import datetime as dt

from pipelines import ingest


def run_trends(config: dict, refresh: bool = False) -> str:
    """Trend scan data: snapshot -> metrics -> charts (deliverable D2)."""
    trends_config = config["trends"]

    if refresh:
        today = dt.date.today()
        counts = ingest.fetch_publication_counts(trends_config)
        snapshot = ingest.save_snapshot(counts, fetch_date=today)
        ingest.save_snapshot_note(snapshot, trends_config, fetch_date=today)
        print(f"  new snapshot written: {snapshot.name}")

    snapshot = ingest.find_latest_snapshot()
    if snapshot is None:
        return "skipped (no snapshot in data/raw/ yet; run with --refresh to fetch one)"

    counts = ingest.load_snapshot(snapshot)

    # TODO (owner, sprint 1): from here on, wire up the analysis:
    #   metrics = transform.compute_trend_metrics(counts, trends_config)
    #   write_csv(metrics, PROCESSED_DIR / "trend_metrics.csv")
    #   save_figure(plot_time_series(...), "trend_time_series")
    #   save_figure(plot_trend_radar(...), "trend_radar")
    return f"snapshot {snapshot.name} loaded ({len(counts)} rows); analysis not wired up yet"


def run_scoring(config: dict, refresh: bool = False) -> str:
    """Opportunity scoring (deliverable D3). Built in sprint 2."""
    # TODO (owner, sprint 2): read the opportunity list, score, run the
    # sensitivity check, write the tables and charts.
    return "skipped (built in sprint 2)"


# Order matters: `run all` goes through this dictionary from top to bottom.
STEPS = {
    "trends": run_trends,
    "scoring": run_scoring,
}
