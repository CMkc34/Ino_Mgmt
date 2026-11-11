"""Step 1: get the source data.

The pipeline never reads from the internet during a normal run. It reads a
*snapshot*: a dated copy of the source data stored in data/raw/. Only
`--refresh` contacts the source and writes a new snapshot (requirement R-1.5).

Snapshot format (one row per sub-topic and year):

    subtopic_id,year,works_count
    predictive_maintenance,2015,1234

File name: publication_counts_YYYY-MM-DD.csv, where the date is the fetch
date. The special sub-topic id "_field" holds the counts for the whole
field (the baseline for relative momentum).
"""

import datetime as dt
from pathlib import Path

import pandas as pd

from pipelines.io import read_csv, write_csv
from pipelines.paths import RAW_DIR

SNAPSHOT_PREFIX = "publication_counts_"
SNAPSHOT_COLUMNS = ["subtopic_id", "year", "works_count"]


def find_latest_snapshot(raw_dir: Path = RAW_DIR) -> Path | None:
    """Return the newest snapshot file, or None if there is none yet.

    The date in the file name is written as YYYY-MM-DD, so sorting the
    names alphabetically also sorts them by date.
    """
    snapshots = sorted(raw_dir.glob(f"{SNAPSHOT_PREFIX}*.csv"))
    return snapshots[-1] if snapshots else None


def load_snapshot(path: Path) -> pd.DataFrame:
    """Read a snapshot and check that it has the expected columns."""
    counts = read_csv(path)
    missing = set(SNAPSHOT_COLUMNS) - set(counts.columns)
    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")
    return counts[SNAPSHOT_COLUMNS]


def save_snapshot(
    counts: pd.DataFrame,
    fetch_date: dt.date,
    raw_dir: Path = RAW_DIR,
) -> Path:
    """Write a new snapshot named after its fetch date and return its path."""
    path = raw_dir / f"{SNAPSHOT_PREFIX}{fetch_date.isoformat()}.csv"
    ordered = counts[SNAPSHOT_COLUMNS].sort_values(["subtopic_id", "year"])
    write_csv(ordered, path)
    return path


def fetch_publication_counts(trends_config: dict) -> pd.DataFrame:
    """Fetch yearly publication counts for every sub-topic from the source.

    TODO (owner, sprint 1): implement this after the data availability check.

    What it has to do:
      1. For the field query and for each sub-topic in
         trends_config["subtopics"], ask the source for the number of works
         per publication year (OpenAlex can group results by year).
      2. Keep only the years from first_year to last_year.
      3. Return one table with the columns in SNAPSHOT_COLUMNS, using the
         sub-topic id "_field" for the field query.

    Rules:
      - Any API key comes from an environment variable, never from the code
        or the config file (acceptance criterion AC-1.8).
      - Stop with a clear error if a sub-topic has an empty query.
    """
    raise NotImplementedError(
        "fetch_publication_counts is not written yet. See the TODO in pipelines/ingest.py."
    )
