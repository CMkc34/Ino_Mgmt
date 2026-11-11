"""Tests for the snapshot handling in pipelines/ingest.py.

`tmp_path` is a temporary folder that pytest creates for each test, so the
tests never touch the real data/raw/ folder.
"""

import datetime as dt

import pandas as pd
import pytest

from pipelines import ingest


def example_counts() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "subtopic_id": ["digital_twins", "digital_twins", "_field"],
            "year": [2024, 2023, 2024],
            "works_count": [120, 100, 5000],
        }
    )


def test_no_snapshot_found_in_an_empty_folder(tmp_path):
    assert ingest.find_latest_snapshot(tmp_path) is None


def test_latest_snapshot_is_the_one_with_the_newest_date(tmp_path):
    ingest.save_snapshot(example_counts(), dt.date(2026, 11, 5), tmp_path)
    newest = ingest.save_snapshot(example_counts(), dt.date(2026, 12, 1), tmp_path)
    assert ingest.find_latest_snapshot(tmp_path) == newest


def test_snapshot_survives_a_save_and_load_round_trip(tmp_path):
    path = ingest.save_snapshot(example_counts(), dt.date(2026, 11, 5), tmp_path)
    loaded = ingest.load_snapshot(path)
    assert len(loaded) == 3
    assert list(loaded.columns) == ingest.SNAPSHOT_COLUMNS
    assert loaded["works_count"].sum() == 5220


def test_saving_the_same_snapshot_twice_gives_identical_files(tmp_path):
    first = ingest.save_snapshot(example_counts(), dt.date(2026, 11, 5), tmp_path).read_bytes()
    second = ingest.save_snapshot(example_counts(), dt.date(2026, 11, 5), tmp_path).read_bytes()
    assert first == second
    assert b"\r\n" not in first  # LF line endings on every operating system


def test_snapshot_with_a_missing_column_is_rejected(tmp_path):
    broken = tmp_path / "publication_counts_2026-11-05.csv"
    broken.write_text("subtopic_id,year\ndigital_twins,2024\n", encoding="utf-8")
    with pytest.raises(ValueError, match="works_count"):
        ingest.load_snapshot(broken)
