"""Tests for pipelines/openalex.py and the fetch in pipelines/ingest.py.

No test here touches the network. A FakeSession stands in for the real
connection: it records what was asked and hands back prepared answers.
"""

import datetime as dt
import json

import pandas as pd
import pytest

from pipelines import ingest, openalex


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


class FakeSession:
    """Returns the prepared responses one after another and records each call."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": params})
        # When only one response is left, keep returning it.
        return self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]


def grouped_answer(counts_by_year):
    groups = [{"key": str(year), "key_display_name": str(year), "count": count} for year, count in counts_by_year.items()]
    return FakeResponse(payload={"meta": {}, "results": [], "group_by": groups})


@pytest.fixture(autouse=True)
def no_credentials_and_no_waiting(monkeypatch):
    """Start every test without credentials, and make pauses instant."""
    monkeypatch.delenv("OPENALEX_API_KEY", raising=False)
    monkeypatch.delenv("OPENALEX_MAILTO", raising=False)
    monkeypatch.setattr("time.sleep", lambda seconds: None)


# --- building filters -------------------------------------------------------


def test_filter_puts_title_blocks_and_text_blocks_in_their_fields():
    filter_text = openalex.build_filter(['"digital twin"'], ["manufacturing OR factory", '"machine learning"'], 2015, 2025)
    assert filter_text == (
        'title.search:("digital twin"),'
        "title_and_abstract.search:(manufacturing OR factory),"
        'title_and_abstract.search:("machine learning"),'
        "publication_year:2015-2025,"
        "is_retracted:false"
    )


def test_filter_can_limit_the_work_types():
    filter_text = openalex.build_filter(["robot"], [], 2024, 2025, work_types=["article", "review"])
    assert "type:article|review" in filter_text


def test_empty_blocks_are_left_out():
    filter_text = openalex.build_filter(["robot", "", "  "], ["factory"], 2024, 2025)
    assert filter_text.count("title.search") == 1


def test_filter_without_any_terms_is_rejected():
    with pytest.raises(ValueError):
        openalex.build_filter([], [" "], 2024, 2025)


@pytest.mark.parametrize("bad_terms", ["robots, cobots", "robots | cobots"])
def test_filter_rejects_characters_with_a_special_meaning(bad_terms):
    with pytest.raises(ValueError):
        openalex.build_filter([bad_terms], [], 2015, 2025)


# --- reading answers --------------------------------------------------------


def test_years_missing_from_the_answer_count_as_zero():
    answer = {"group_by": [{"key": "2024", "count": 7}]}
    assert openalex.parse_year_counts(answer, 2023, 2025) == {2023: 0, 2024: 7, 2025: 0}


def test_years_outside_the_range_are_ignored():
    answer = {"group_by": [{"key": "2010", "count": 99}, {"key": "2024", "count": 7}]}
    assert openalex.parse_year_counts(answer, 2024, 2025) == {2024: 7, 2025: 0}


def test_answer_without_groups_is_reported():
    with pytest.raises(openalex.OpenAlexError):
        openalex.parse_year_counts({"results": []}, 2024, 2025)


# --- sending requests -------------------------------------------------------


def test_request_asks_for_counts_grouped_by_year():
    session = FakeSession([grouped_answer({2024: 5})])
    counts = openalex.fetch_year_counts("title.search:(a),publication_year:2024-2025", 2024, 2025, session)
    assert counts == {2024: 5, 2025: 0}
    sent = session.calls[0]
    assert sent["url"] == openalex.API_URL
    assert sent["params"]["group_by"] == "publication_year"
    assert sent["params"]["filter"] == "title.search:(a),publication_year:2024-2025"
    assert "api_key" not in sent["params"]


def test_credentials_come_from_environment_variables(monkeypatch):
    monkeypatch.setenv("OPENALEX_API_KEY", "secret-key")
    monkeypatch.setenv("OPENALEX_MAILTO", "someone@example.org")
    session = FakeSession([grouped_answer({2024: 5})])
    openalex.fetch_year_counts("title.search:(a)", 2024, 2024, session)
    assert session.calls[0]["params"]["api_key"] == "secret-key"
    assert session.calls[0]["params"]["mailto"] == "someone@example.org"


def test_temporary_errors_are_retried():
    session = FakeSession([FakeResponse(429), FakeResponse(503), grouped_answer({2024: 5})])
    assert openalex.fetch_year_counts("title.search:(a)", 2024, 2024, session) == {2024: 5}
    assert len(session.calls) == 3


def test_gives_up_after_repeated_temporary_errors():
    session = FakeSession([FakeResponse(503)])
    with pytest.raises(openalex.OpenAlexError, match="did not answer"):
        openalex.fetch_year_counts("title.search:(a)", 2024, 2024, session)
    assert len(session.calls) == openalex.MAX_ATTEMPTS


def test_refused_request_points_to_the_api_key_and_is_not_retried():
    session = FakeSession([FakeResponse(403)])
    with pytest.raises(openalex.OpenAlexError, match="OPENALEX_API_KEY"):
        openalex.fetch_year_counts("title.search:(a)", 2024, 2024, session)
    assert len(session.calls) == 1


def test_used_up_free_allowance_points_to_the_api_key_and_is_not_retried():
    session = FakeSession([FakeResponse(429, text='{"error":"Rate limit exceeded","message":"Insufficient budget."}')])
    with pytest.raises(openalex.OpenAlexError, match="OPENALEX_API_KEY"):
        openalex.fetch_year_counts("title.search:(a)", 2024, 2024, session)
    assert len(session.calls) == 1


def test_bad_query_is_reported_and_not_retried():
    session = FakeSession([FakeResponse(400, text="Invalid query")])
    with pytest.raises(openalex.OpenAlexError, match="Invalid query"):
        openalex.fetch_year_counts("title.search:(a)", 2024, 2024, session)
    assert len(session.calls) == 1


def test_sample_returns_id_title_and_year():
    works = [{"id": "https://openalex.org/W1", "display_name": "A paper", "publication_year": 2024, "type": "article"}]
    session = FakeSession([FakeResponse(payload={"results": works})])
    sample = openalex.fetch_sample("title.search:(a)", size=20, seed=42, session=session)
    assert sample == [{"id": "https://openalex.org/W1", "title": "A paper", "year": 2024, "type": "article"}]
    assert session.calls[0]["params"]["sample"] == 20
    assert session.calls[0]["params"]["seed"] == 42


# --- the fetch as a whole ---------------------------------------------------


def small_config():
    return {
        "source": "OpenAlex",
        "first_year": 2024,
        "last_year": 2025,
        "growth_window_years": 1,
        "work_types": ["article"],
        "context_terms": "manufacturing",
        "ai_terms": '"machine learning"',
        "subtopics": [
            {"id": "digital_twins", "label": "Digital twins", "title_terms": '"digital twin"'},
            {"id": "robots", "label": "Robots", "title_terms": "robot", "title_also": "assembly", "title_ai_terms": "learning"},
        ],
    }


def test_fetch_returns_one_row_per_subtopic_and_year_plus_the_field():
    session = FakeSession([grouped_answer({2024: 10, 2025: 20})])
    counts = ingest.fetch_publication_counts(small_config(), session)
    assert list(counts.columns) == ingest.SNAPSHOT_COLUMNS
    assert len(counts) == 6  # (field + 2 sub-topics) x 2 years
    assert set(counts["subtopic_id"]) == {"_field", "digital_twins", "robots"}
    assert len(session.calls) == 3  # one request per query


def test_field_filter_has_no_title_condition_and_subtopics_are_subsets_of_it():
    filters = ingest.build_filters(small_config())
    field_conditions = filters["_field"].split(",")
    assert not any(condition.startswith("title.search") for condition in field_conditions)
    # A sub-topic filter is the field filter plus its title conditions.
    for subtopic_id in ("digital_twins", "robots"):
        assert set(field_conditions) <= set(filters[subtopic_id].split(","))
    assert filters["digital_twins"].startswith('title.search:("digital twin"),')
    assert "title.search:(robot),title.search:(assembly),title.search:(learning)," in filters["robots"]


def test_filters_can_be_built_for_other_years():
    filters = ingest.build_filters(small_config(), first_year=2023, last_year=2025)
    assert "publication_year:2023-2025" in filters["robots"]


def test_subtopic_without_terms_stops_the_fetch():
    config = small_config()
    config["subtopics"][0]["title_terms"] = ""
    with pytest.raises(ValueError, match="digital_twins"):
        ingest.fetch_publication_counts(config, FakeSession([grouped_answer({})]))


def test_snapshot_note_records_source_date_and_queries(tmp_path):
    snapshot = tmp_path / "publication_counts_2026-11-12.csv"
    note_path = ingest.save_snapshot_note(snapshot, small_config(), dt.date(2026, 11, 12))
    assert note_path.name == "publication_counts_2026-11-12.meta.json"
    note = json.loads(note_path.read_text(encoding="utf-8"))
    assert note["source"] == "OpenAlex"
    assert note["fetch_date"] == "2026-11-12"
    assert set(note["filters"]) == {"_field", "digital_twins", "robots"}
    assert b"\r\n" not in note_path.read_bytes()


# --- robustness variants and the discovery step -----------------------------


def test_variant_without_ai_drops_every_ai_condition():
    filters = ingest.build_filters(small_config(), variant="no_ai")
    assert "machine learning" not in filters["_field"]
    assert "title.search:(learning)" not in filters["robots"]
    assert "title.search:(robot),title.search:(assembly)," in filters["robots"]


def test_variant_articles_counts_only_articles():
    config = small_config()
    config["work_types"] = ["article", "review", "preprint"]
    filters = ingest.build_filters(config, variant="articles")
    assert all("type:article," in filter_text for filter_text in filters.values())


def test_unknown_variant_is_rejected():
    with pytest.raises(ValueError, match="unknown variant"):
        ingest.build_filters(small_config(), variant="typo")


def test_variant_snapshots_do_not_hide_the_main_snapshot(tmp_path):
    counts = ingest.fetch_publication_counts(small_config(), FakeSession([grouped_answer({2024: 1})]))
    main = ingest.save_snapshot(counts, dt.date(2026, 11, 12), tmp_path)
    for prefix in ("robustness_no_ai_counts_", "robustness_articles_counts_"):
        ingest.save_snapshot(counts, dt.date(2026, 12, 1), tmp_path, prefix=prefix)
    assert ingest.find_latest_snapshot(tmp_path) == main
    assert ingest.find_latest_snapshot(tmp_path, "robustness_no_ai_counts_").name == "robustness_no_ai_counts_2026-12-01.csv"


def topic_answer(topics):
    groups = [{"key": key, "key_display_name": name, "count": count} for key, name, count in topics]
    return FakeResponse(payload={"group_by": groups})


def test_discovery_combines_the_two_years_and_leaves_unknown_counts_empty(tmp_path):
    session = FakeSession(
        [
            topic_answer([("T1", "Scheduling", 40), ("T2", "Welding", 35)]),  # first year
            topic_answer([("T1", "Scheduling", 90), ("T3", "Language models", 70)]),  # last year
        ]
    )
    table = ingest.fetch_discovery_topics(small_config(), session)
    rows = {row["topic_id"]: row for row in table.to_dict("records")}
    assert rows["T1"]["works_first_year"] == 40 and rows["T1"]["works_last_year"] == 90
    assert pd.isna(rows["T2"]["works_last_year"])
    assert pd.isna(rows["T3"]["works_first_year"])
    assert "publication_year:2024-2024" in session.calls[0]["params"]["filter"]
    assert "publication_year:2025-2025" in session.calls[1]["params"]["filter"]

    path = ingest.save_discovery_topics(table, dt.date(2026, 11, 12), tmp_path)
    assert path.name == "discovery_topics_2026-11-12.csv"
    assert path.read_text(encoding="utf-8").splitlines()[0] == "topic_id,topic_name,works_first_year,works_last_year"
