"""Talking to OpenAlex (https://openalex.org), an open index of research works.

Only this file knows how the OpenAlex web service works. The rest of the
pipeline just receives tables, so switching to another source later means
replacing this one file.

How a request works
-------------------
We ask the "works" endpoint for all works that meet a set of conditions
(words in the title, words in the title or abstract, publication years,
work types) and tell it to group the result by publication year. The answer
contains one count per year, so one request per sub-topic is enough.

Credentials
-----------
Optional, and read from environment variables only (acceptance criterion
AC-1.8). Never put them in the code or in config.yaml.

    OPENALEX_API_KEY   a free API key. Without one, requests share a small
                       daily allowance with everyone on the same network
                       address, which is often already used up.
    OPENALEX_MAILTO    a contact email; OpenAlex asks for one as a courtesy

Verified against the live service on 2026-11-12: the request format, the
handling of AND / OR / quoted phrases, and the sample. OpenAlex matches
word stems, so "robot" also finds "robots".
"""

import os
import time

import requests

API_URL = "https://api.openalex.org/works"
TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 4

# The two places a search can look. Title only is strict: the work is
# *about* the term. Title and abstract is loose: the term is mentioned.
# (The full-text search is not used: it also matches passing mentions deep
# inside a paper.)
TITLE_FIELD = "title.search"
TEXT_FIELD = "title_and_abstract.search"

# In an OpenAlex filter, a comma separates conditions and a pipe means "or",
# so neither may appear inside a block of search terms.
FORBIDDEN_CHARACTERS = [",", "|"]


class OpenAlexError(RuntimeError):
    """A request to OpenAlex failed in a way that retrying will not fix."""


def check_terms(terms: str) -> str:
    """Return the terms unchanged, or stop if they would break the filter."""
    for character in FORBIDDEN_CHARACTERS:
        if character in terms:
            raise ValueError(
                f"search terms must not contain {character!r} (it has a special meaning in an OpenAlex filter): {terms}"
            )
    return terms.strip()


def build_filter(
    title_blocks: list[str],
    text_blocks: list[str],
    first_year: int,
    last_year: int,
    work_types: list[str] | None = None,
) -> str:
    """Build the OpenAlex filter text. All conditions must hold together.

    title_blocks   each block of terms must be found in the title
    text_blocks    each block must be found in the title or the abstract
    work_types     if given, only these types of work are counted
    Retracted works are always left out.
    """
    conditions = [f"{TITLE_FIELD}:({check_terms(block)})" for block in title_blocks if block and block.strip()]
    conditions += [f"{TEXT_FIELD}:({check_terms(block)})" for block in text_blocks if block and block.strip()]
    if not conditions:
        raise ValueError("a query needs at least one block of search terms")
    conditions.append(f"publication_year:{first_year}-{last_year}")
    if work_types:
        conditions.append("type:" + "|".join(work_types))
    conditions.append("is_retracted:false")
    return ",".join(conditions)


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
            if status == 429 and "budget" in response.text.lower():
                # Not a "slow down" signal: the free allowance is used up,
                # so waiting a few seconds and retrying cannot help.
                raise OpenAlexError(
                    "OpenAlex's free allowance for requests without a key is used up. Get a free API key "
                    "(https://help.openalex.org/api/authentication/), set the environment variable "
                    "OPENALEX_API_KEY and try again."
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


def fetch_year_counts(filter_text: str, first_year: int, last_year: int, session=None) -> dict[int, int]:
    """Number of works per publication year that meet a filter."""
    parameters = {"filter": filter_text, "group_by": "publication_year"}
    return parse_year_counts(request_json(parameters, session), first_year, last_year)


def fetch_group_counts(filter_text: str, group_by: str, session=None) -> list[dict]:
    """Count works that meet a filter, grouped by a property (e.g. their topic).

    Returns up to 200 groups, largest first, each with key, name and count.
    """
    answer = request_json({"filter": filter_text, "group_by": group_by, "per-page": 200}, session)
    if "group_by" not in answer:
        raise OpenAlexError("unexpected answer from OpenAlex: it has no 'group_by' part")
    return [
        {"key": group["key"], "name": group.get("key_display_name"), "count": int(group["count"])}
        for group in answer["group_by"]
    ]


def fetch_sample(filter_text: str, size: int = 20, seed: int = 42, session=None) -> list[dict]:
    """A random sample of works that meet a filter, for the query-quality check (R-2.6).

    The fixed seed means the same filter returns the same sample, so the
    check can be repeated. Each item has the keys id, title, year and type.
    """
    parameters = {
        "filter": filter_text,
        "sample": size,
        "seed": seed,
        "per-page": size,
        "select": "id,display_name,publication_year,type",
    }
    answer = request_json(parameters, session)
    return [
        {
            "id": work.get("id"),
            "title": work.get("display_name"),
            "year": work.get("publication_year"),
            "type": work.get("type"),
        }
        for work in answer.get("results", [])
    ]
