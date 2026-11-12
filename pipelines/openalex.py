"""Talking to OpenAlex (https://openalex.org), an open index of research works.

Only this file knows how the OpenAlex web service works. The rest of the
pipeline just receives tables, so switching to another source later means
replacing this one file.

How a request works
-------------------
We ask the "works" endpoint for all works that match a search in their
title or abstract and were published in a range of years, and tell it to
group the result by publication year. The answer contains one count per
year, so one request per sub-topic is enough.

Credentials
-----------
Optional, and read from environment variables only (acceptance criterion
AC-1.8). Never put them in the code or in config.yaml.

    OPENALEX_API_KEY   an API key, if OpenAlex requires one for your usage
    OPENALEX_MAILTO    a contact email; OpenAlex asks for one as a courtesy
"""

import os
import time

import requests

API_URL = "https://api.openalex.org/works"
TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 4

# The field that is searched. Title and abstract only: the full-text search
# also matches works that merely mention a term in passing.
SEARCH_FIELD = "title_and_abstract.search"

# In an OpenAlex filter, a comma separates conditions and a pipe means "or",
# so neither may appear inside a search query.
FORBIDDEN_CHARACTERS = [",", "|"]


class OpenAlexError(RuntimeError):
    """A request to OpenAlex failed in a way that retrying will not fix."""


def compose_query(terms: str, context_terms: str, ai_terms: str) -> str:
    """Combine the three building blocks of a query with AND.

    Every sub-topic query has the same shape:

        (sub-topic terms) AND (manufacturing context) AND (AI terms)

    The field baseline is the same without the first block, so every
    sub-topic is a subset of the field.
    """
    blocks = [terms, context_terms, ai_terms]
    blocks = [block.strip() for block in blocks if block and block.strip()]
    if not blocks:
        raise ValueError("a query needs at least one block of search terms")
    return " AND ".join(f"({block})" for block in blocks)


def build_filter(query: str, first_year: int, last_year: int) -> str:
    """Build the OpenAlex filter text for a query and a range of years."""
    for character in FORBIDDEN_CHARACTERS:
        if character in query:
            raise ValueError(
                f"search queries must not contain {character!r} (it has a special meaning in an OpenAlex filter): {query}"
            )
    return f"{SEARCH_FIELD}:{query},publication_year:{first_year}-{last_year}"


def credentials_from_environment() -> dict:
    """Return the optional credential parameters set in the environment."""
    parameters = {}
    if os.environ.get("OPENALEX_API_KEY"):
        parameters["api_key"] = os.environ["OPENALEX_API_KEY"]
    if os.environ.get("OPENALEX_MAILTO"):
        parameters["mailto"] = os.environ["OPENALEX_MAILTO"]
    return parameters


def request_json(parameters: dict, session=None, wait_seconds: float = 2.0) -> dict:
    """Send one request to OpenAlex and return the decoded answer.

    Temporary problems (too many requests, server errors, network hiccups)
    are retried a few times with a growing pause. Problems that a retry
    cannot fix stop with a message that says what to do.

    `session` is anything with a `.get()` method that behaves like
    requests.Session. The tests pass in a fake one, so they need no network.
    """
    session = session or requests.Session()
    parameters = {**parameters, **credentials_from_environment()}

    last_problem = "no attempt made"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = session.get(API_URL, params=parameters, timeout=TIMEOUT_SECONDS)
        except requests.RequestException as error:
            last_problem = f"network problem: {error}"
        else:
            status = response.status_code
            if status == 200:
                return response.json()
            if status in (401, 403):
                raise OpenAlexError(
                    f"OpenAlex refused the request (HTTP {status}). It may need an API key: "
                    "set the environment variable OPENALEX_API_KEY and try again."
                )
            if status == 429 or status >= 500:
                last_problem = f"HTTP {status}"
            else:
                raise OpenAlexError(
                    f"OpenAlex rejected the request (HTTP {status}). Check the query: {response.text[:300]}"
                )
        if attempt < MAX_ATTEMPTS:
            time.sleep(wait_seconds * attempt)

    raise OpenAlexError(f"OpenAlex did not answer after {MAX_ATTEMPTS} attempts ({last_problem}).")


def parse_year_counts(answer: dict, first_year: int, last_year: int) -> dict[int, int]:
    """Turn a grouped answer into {year: number of works}.

    OpenAlex leaves out years with no works, so every year in the range
    starts at 0 and is then filled in from the answer.
    """
    if "group_by" not in answer:
        raise OpenAlexError("unexpected answer from OpenAlex: it has no 'group_by' part")

    counts = {year: 0 for year in range(first_year, last_year + 1)}
    for group in answer["group_by"]:
        year = int(group["key"])
        if year in counts:
            counts[year] = int(group["count"])
    return counts


def fetch_year_counts(query: str, first_year: int, last_year: int, session=None) -> dict[int, int]:
    """Number of works per publication year that match a query."""
    parameters = {
        "filter": build_filter(query, first_year, last_year),
        "group_by": "publication_year",
    }
    return parse_year_counts(request_json(parameters, session), first_year, last_year)


def fetch_sample(query: str, first_year: int, last_year: int, size: int = 20, seed: int = 42, session=None) -> list[dict]:
    """A random sample of matching works, for the query-quality check (R-2.6).

    The fixed seed means the same query returns the same sample, so the
    check can be repeated. Each item has the keys id, title and year.
    """
    parameters = {
        "filter": build_filter(query, first_year, last_year),
        "sample": size,
        "seed": seed,
        "per-page": size,
        "select": "id,display_name,publication_year",
    }
    answer = request_json(parameters, session)
    return [
        {"id": work.get("id"), "title": work.get("display_name"), "year": work.get("publication_year")}
        for work in answer.get("results", [])
    ]
