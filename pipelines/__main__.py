"""Command line entry point.

    python -m pipelines run all            run every step
    python -m pipelines run trends         run one step
    python -m pipelines run all --refresh  fetch new source data first
"""

import argparse
import sys

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
    return parser


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    config = load_config()

    step_names = list(STEPS) if args.step == "all" else [args.step]
    for name in step_names:
        print(f"[{name}]")
        status = STEPS[name](config, refresh=args.refresh)
        print(f"  {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
