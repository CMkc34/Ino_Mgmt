"""Step 1: get the source data.

The pipeline never reads from the internet during a normal run. It reads a
*snapshot*: a dated copy of the source data stored in data/raw/. Only
`--refresh` contacts the source and writes a new snapshot (requirement R-1.5).

Snapshot format (one row per sub-topic and year):

    subtopic_id,year,works_count
    predictive_maintenance,2015,1234

File name: publication_counts_YYYY-MM-DD.csv, where the date is the fetch
date. The special sub-topic id "_field" holds the counts for the whole
field (the baseline for relative momentum). Next to each snapshot sits a
note, publication_counts_YYYY-MM-DD.meta.json, with the source, the fetch
date and the queries used.
"""

import datetime as dt
import json
import time
from pathlib import Path

import pandas as pd

from pipelines import openalex
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


FIELD_ID = "_field"


def composed_queries(trends_config: dict) -> dict[str, str]:
    """Return {sub-topic id: full search query}, including the field baseline.

    Stops with a clear message if a sub-topic has no search terms.
    """
    context_terms = trends_config["context_terms"]
    ai_terms = trends_config["ai_terms"]

    queries = {FIELD_ID: openalex.compose_query("", context_terms, ai_terms)}
    for subtopic in trends_config["subtopics"]:
        if not str(subtopic.get("terms") or "").strip():
            raise ValueError(f"sub-topic '{subtopic['id']}' has no search terms in config.yaml")
        queries[subtopic["id"]] = openalex.compose_query(subtopic["terms"], context_terms, ai_terms)
    return queries


def fetch_publication_counts(trends_config: dict, session=None, pause_seconds: float = 0.2) -> pd.DataFrame:
    """Fetch yearly publication counts for the field and every sub-topic.

    Returns one table with the columns in SNAPSHOT_COLUMNS. The field
    baseline uses the sub-topic id "_field". One request is sent per query,
    with a short pause in between to be polite to the service.
    """
    first_year = trends_config["first_year"]
    last_year = trends_config["last_year"]

    rows = []
    for subtopic_id, query in composed_queries(trends_config).items():
        year_counts = openalex.fetch_year_counts(query, first_year, last_year, session)
        for year, works_count in year_counts.items():
            rows.append({"subtopic_id": subtopic_id, "year": year, "works_count": works_count})
        time.sleep(pause_seconds)
    return pd.DataFrame(rows, columns=SNAPSHOT_COLUMNS)


def save_snapshot_note(snapshot_path: Path, trends_config: dict, fetch_date: dt.date) -> Path:
    """Write the companion note for a snapshot (requirement R-1.6).

    The note records where the data came from, when it was fetched and the
    exact queries used, so the numbers can be traced and re-fetched.
    """
    note = {
        "source": trends_config["source"],
        "endpoint": openalex.API_URL,
        "search_field": openalex.SEARCH_FIELD,
        "fetch_date": fetch_date.isoformat(),
        "first_year": trends_config["first_year"],
        "last_year": trends_config["last_year"],
        "queries": composed_queries(trends_config),
    }
    note_path = snapshot_path.with_suffix(".meta.json")
    text = json.dumps(note, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    note_path.write_text(text, encoding="utf-8", newline="\n")
    return note_path
