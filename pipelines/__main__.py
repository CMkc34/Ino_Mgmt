"""Command line entry point.

    python -m pipelines run all            run every step
    python -m pipelines run trends         run one step
    python -m pipelines run all --refresh  fetch new source data first
    python -m pipelines sample digital_twins   list 20 random works for a
                                               sub-topic (query-quality check)
"""

import argparse
import sys

from pipelines import ingest, openalex
from pipelines.config import load_config
from pipelines.steps import STEPS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m pipelines")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="run one pipeline step, or all of them")
    run.add_argument("step", choices=["all", *STEPS], help="which step to run")
    run.add_argument(
        "--refresh",
        action="store_true",
        help="fetch new data from the source and write a new snapshot (needs network access)",
    )

    sample = commands.add_parser(
        "sample",
        help="list random works that match a sub-topic query (needs network access)",
    )
    sample.add_argument("subtopic_id", help="a sub-topic id from config.yaml, or _field")
    sample.add_argument("--size", type=int, default=20, help="number of works (default 20)")
    return parser


def print_sample(config: dict, subtopic_id: str, size: int) -> int:
    """Print random recent works for one sub-topic, to judge the query by hand."""
    trends_config = config["trends"]

    # Sample from the same years that the "volume" metric uses.
    last_year = trends_config["last_year"]
    first_year = last_year - trends_config["volume_window_years"] + 1
    filters = ingest.build_filters(trends_config, first_year, last_year)

    if subtopic_id not in filters:
        print(f"unknown sub-topic '{subtopic_id}'. Known ids: {', '.join(filters)}")
        return 1

    print(f"filter: {filters[subtopic_id]}\n")
    works = openalex.fetch_sample(filters[subtopic_id], size=size)
    for number, work in enumerate(works, start=1):
        print(f"{number:>2}. [{work['year']} {work['type']}] {work['title']}")
        print(f"    {work['id']}")
    return 0


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    config = load_config()

    try:
        if args.command == "sample":
            return print_sample(config, args.subtopic_id, args.size)

        step_names = list(STEPS) if args.step == "all" else [args.step]
        for name in step_names:
            print(f"[{name}]")
            status = STEPS[name](config, refresh=args.refresh)
            print(f"  {status}")
    except openalex.OpenAlexError as error:
        # A problem with the data source: show the message, not a traceback.
        print(f"error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
