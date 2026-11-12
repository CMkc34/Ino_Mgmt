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


def find_latest_snapshot(raw_dir: Path = RAW_DIR, prefix: str = SNAPSHOT_PREFIX) -> Path | None:
    """Return the newest snapshot file, or None if there is none yet.

    The date in the file name is written as YYYY-MM-DD, so sorting the
    names alphabetically also sorts them by date.
    """
    snapshots = sorted(raw_dir.glob(f"{prefix}*.csv"))
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
    prefix: str = SNAPSHOT_PREFIX,
) -> Path:
    """Write a new snapshot named after its fetch date and return its path."""
    path = raw_dir / f"{prefix}{fetch_date.isoformat()}.csv"
    ordered = counts[SNAPSHOT_COLUMNS].sort_values(["subtopic_id", "year"])
    write_csv(ordered, path)
    return path


FIELD_ID = "_field"


# The main counts and the two robustness variants of the approved method
# (docs/design/trend-scan-method.md, section 7). Each variant is stored in
# its own snapshot file, named with the prefix given here.
VARIANTS = {
    "main": "publication_counts_",
    "no_ai": "robustness_no_ai_counts_",        # test D: without the AI terms
    "articles": "robustness_articles_counts_",  # test C: work type "article" only
}


def build_filters(
    trends_config: dict,
    first_year: int | None = None,
    last_year: int | None = None,
    variant: str = "main",
) -> dict[str, str]:
    """Return {sub-topic id: OpenAlex filter}, including the field baseline.

    The field baseline counts works that mention a manufacturing term and
    an AI term in their title or abstract.

    A sub-topic counts works that
      - have the sub-topic's terms in the TITLE (so the work is about it),
      - also have the optional blocks `title_also` and `title_ai_terms` in
        the title,
      - and meet the field conditions.
    Every sub-topic is therefore a subset of the field.

    Variants:
      "no_ai"     drops every AI condition, for the field and the sub-topics
      "articles"  counts only works of the type "article"

    The years default to the full range in the configuration.
    """
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant '{variant}'. Known: {', '.join(VARIANTS)}")
    first_year = first_year or trends_config["first_year"]
    last_year = last_year or trends_config["last_year"]
    work_types = ["article"] if variant == "articles" else trends_config.get("work_types")
    with_ai = variant != "no_ai"

    field_blocks = [trends_config["context_terms"]]
    if with_ai:
        field_blocks.append(trends_config["ai_terms"])

    filters = {FIELD_ID: openalex.build_filter([], field_blocks, first_year, last_year, work_types)}
    for subtopic in trends_config["subtopics"]:
        if not str(subtopic.get("title_terms") or "").strip():
            raise ValueError(f"sub-topic '{subtopic['id']}' has no title_terms in config.yaml")
        title_blocks = [subtopic["title_terms"], subtopic.get("title_also") or ""]
        if with_ai:
            title_blocks.append(subtopic.get("title_ai_terms") or "")
        filters[subtopic["id"]] = openalex.build_filter(title_blocks, field_blocks, first_year, last_year, work_types)
    return filters


def fetch_publication_counts(
    trends_config: dict, session=None, pause_seconds: float = 0.2, variant: str = "main"
) -> pd.DataFrame:
    """Fetch yearly publication counts for the field and every sub-topic.

    Returns one table with the columns in SNAPSHOT_COLUMNS. The field
    baseline uses the sub-topic id "_field". One request is sent per filter,
    with a short pause in between to be polite to the service.
    """
    first_year = trends_config["first_year"]
    last_year = trends_config["last_year"]

    rows = []
    for subtopic_id, filter_text in build_filters(trends_config, variant=variant).items():
        year_counts = openalex.fetch_year_counts(filter_text, first_year, last_year, session)
        for year, works_count in year_counts.items():
            rows.append({"subtopic_id": subtopic_id, "year": year, "works_count": works_count})
        time.sleep(pause_seconds)
    return pd.DataFrame(rows, columns=SNAPSHOT_COLUMNS)


def save_snapshot_note(
    snapshot_path: Path, trends_config: dict, fetch_date: dt.date, variant: str = "main"
) -> Path:
    """Write the companion note for a snapshot (requirement R-1.6).

    The note records where the data came from, when it was fetched and the
    exact filters used, so the numbers can be traced and re-fetched.
    """
    note = {
        "source": trends_config["source"],
        "endpoint": openalex.API_URL,
        "fetch_date": fetch_date.isoformat(),
        "first_year": trends_config["first_year"],
        "last_year": trends_config["last_year"],
        "variant": variant,
        "filters": build_filters(trends_config, variant=variant),
    }
    note_path = snapshot_path.with_suffix(".meta.json")
    text = json.dumps(note, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    note_path.write_text(text, encoding="utf-8", newline="\n")
    return note_path


# --- discovery step (method note, section 6.4) -------------------------------

DISCOVERY_PREFIX = "discovery_topics_"
DISCOVERY_COLUMNS = ["topic_id", "topic_name", "works_first_year", "works_last_year"]


def fetch_discovery_topics(trends_config: dict, session=None) -> pd.DataFrame:
    """Count the source's own topic labels within the field, for two years.

    The two years are the ends of the growth window (2020 and 2025 with the
    current configuration). For each year the source returns its 200 most
    frequent topics. A topic missing from one year's list was below that
    list's smallest count; its cell is left empty.
    """
    last_year = trends_config["last_year"]
    first_year = last_year - trends_config["growth_window_years"]
    counts: dict[str, dict] = {}
    for year, column in ((first_year, "works_first_year"), (last_year, "works_last_year")):
        filter_text = build_filters(trends_config, year, year)[FIELD_ID]
        for topic in openalex.fetch_group_counts(filter_text, "primary_topic.id", session):
            row = counts.setdefault(topic["key"], {"topic_id": topic["key"], "topic_name": topic["name"]})
            row[column] = topic["count"]
        time.sleep(0.2)
    table = pd.DataFrame(list(counts.values()), columns=DISCOVERY_COLUMNS)
    for column in ("works_first_year", "works_last_year"):
        table[column] = table[column].astype("Int64")  # whole numbers, empty where unknown
    return table.sort_values("topic_id").reset_index(drop=True)


def save_discovery_topics(table: pd.DataFrame, fetch_date: dt.date, raw_dir: Path = RAW_DIR) -> Path:
    """Write the discovery table named after its fetch date and return its path."""
    path = raw_dir / f"{DISCOVERY_PREFIX}{fetch_date.isoformat()}.csv"
    write_csv(table[DISCOVERY_COLUMNS], path)
    return path
