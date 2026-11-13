"""Tests for the configuration file and the command line entry point."""

import pytest

from pipelines import ingest
from pipelines.__main__ import main
from pipelines.config import load_config


def test_scoring_weights_sum_to_one():
    weights = load_config()["scoring"]["weights"]
    assert sum(weights.values()) == pytest.approx(1.0)


def test_subtopic_ids_are_unique():
    subtopics = load_config()["trends"]["subtopics"]
    ids = [subtopic["id"] for subtopic in subtopics]
    assert len(ids) == len(set(ids))


def test_number_of_subtopics_is_within_the_required_range():
    # Requirement R-2.2: the trend scan covers 8 to 12 sub-topics.
    assert 8 <= len(load_config()["trends"]["subtopics"]) <= 12


def test_every_subtopic_in_the_config_gives_a_valid_filter():
    # Building the filters rejects empty terms, commas and pipes.
    trends = load_config()["trends"]
    filters = ingest.build_filters(trends)
    assert len(filters) == len(trends["subtopics"]) + 1  # plus the field baseline


def test_default_run_finishes_without_error():
    assert main(["run", "all"]) == 0


def test_unknown_step_is_rejected():
    with pytest.raises(SystemExit):
        main(["run", "no_such_step"])


def test_trends_step_writes_one_result_row_per_subtopic():
    # The default run above has written the result table from the stored snapshot.
    from pipelines.io import read_csv
    from pipelines.paths import FIGURES_DIR, PROCESSED_DIR

    assert main(["run", "trends"]) == 0
    results = read_csv(PROCESSED_DIR / "trend_metrics.csv")
    assert set(results["subtopic_id"]) == {subtopic["id"] for subtopic in load_config()["trends"]["subtopics"]}
    assert (FIGURES_DIR / "trend_map.png").exists()
    assert (FIGURES_DIR / "trend_time_series.png").exists()
