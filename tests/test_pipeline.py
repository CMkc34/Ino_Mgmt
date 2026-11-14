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


def test_scoring_step_runs_on_the_configured_input_set():
    from pipelines.io import read_csv
    from pipelines.paths import FIGURES_DIR, PROCESSED_DIR, in_repo

    scoring_config = load_config()["scoring"]
    assert (in_repo(scoring_config["input_dir"]) / "scores.csv").exists()
    assert main(["run", "scoring"]) == 0
    ranking = read_csv(PROCESSED_DIR / "scoring_ranking.csv")
    assert set(ranking["classification"]) <= {"pursue", "explore", "park"}
    assert (FIGURES_DIR / "scoring_rank_stability.png").exists()
    assert (FIGURES_DIR / "scoring_time_horizon.png").exists()


def test_the_example_set_runs_through_the_model_by_changing_only_the_input_folder():
    # Acceptance criterion AC-3.8: another input set needs no code change.
    from pipelines import scoring
    from pipelines.paths import in_repo

    scoring_config = load_config()["scoring"]
    example = in_repo("tools/opportunity-scoring/example")
    opportunities, scores, business_case = scoring.load_inputs(example, scoring_config["weights"])
    ranking = scoring.build_ranking(opportunities, scores, scoring_config)
    assert list(ranking["id"]) == ["A", "B", "C", "D", "E"]
    assert list(ranking["classification"]) == ["pursue", "pursue", "explore", "park", "park"]
    assert business_case is not None


def test_second_scan_is_configured_like_the_first():
    # Same method and thresholds, so the two scans can be compared.
    config = load_config()
    first, second = config["trends"], config["trends_medtech"]
    for key in ("first_year", "last_year", "volume_window_years", "growth_window_years",
                "emerging_threshold", "quality_threshold", "discovery_top_n", "work_types"):
        assert first[key] == second[key], key
    assert 8 <= len(second["subtopics"]) <= 12
    assert len(ingest.build_filters(second)) == len(second["subtopics"]) + 1


def test_second_scan_keeps_its_files_apart_from_the_first():
    from pipelines.io import read_csv
    from pipelines.paths import PROCESSED_DIR

    assert main(["run", "trends_medtech"]) == 0
    first = set(read_csv(PROCESSED_DIR / "trend_metrics.csv")["subtopic_id"])
    second = set(read_csv(PROCESSED_DIR / "medtech" / "trend_metrics.csv")["subtopic_id"])
    assert second == {subtopic["id"] for subtopic in load_config()["trends_medtech"]["subtopics"]}
    assert not first & second


def test_sample_command_rejects_an_unknown_scan():
    assert main(["sample", "endoscopy", "--scan", "no_such_scan"]) == 1
