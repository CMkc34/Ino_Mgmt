"""Tests for the configuration file and the command line entry point."""

import pytest

from pipelines import ingest, openalex
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


def test_every_subtopic_in_the_config_gives_a_valid_query():
    # Builds the filter for each query, which rejects commas and pipes.
    trends = load_config()["trends"]
    queries = ingest.composed_queries(trends)
    assert len(queries) == len(trends["subtopics"]) + 1  # plus the field baseline
    for query in queries.values():
        openalex.build_filter(query, trends["first_year"], trends["last_year"])


def test_default_run_finishes_without_error():
    assert main(["run", "all"]) == 0


def test_unknown_step_is_rejected():
    with pytest.raises(SystemExit):
        main(["run", "no_such_step"])
