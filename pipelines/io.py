"""Reading and writing data files in a reproducible way.

"Reproducible" here means: writing the same data twice gives a
byte-identical file on every operating system. That is what lets
`git status` stay clean after a pipeline run (acceptance criterion AC-1.3).
"""

from pathlib import Path

import pandas as pd


def write_csv(data: pd.DataFrame, path: Path) -> None:
    """Write a table as CSV with fixed formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(
        path,
        index=False,
        encoding="utf-8",
        lineterminator="\n",   # same line endings on Windows and Linux
        float_format="%.6f",   # same number of decimals everywhere
    )


def read_csv(path: Path) -> pd.DataFrame:
    """Read a CSV file written by write_csv."""
    return pd.read_csv(path, encoding="utf-8")
