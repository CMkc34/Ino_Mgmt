"""Compare each chart in the working folder with the version in the last commit.

Used by the automatic checks to explain a failure: when the pipeline has
redrawn a chart, this prints how much the two pictures differ.

    python tools/compare_charts.py
"""

import io
import subprocess
import sys
from pathlib import Path

from matplotlib import image

FIGURES = Path("outputs/figures")


def main() -> int:
    for path in sorted(FIGURES.glob("*.png")):
        committed = subprocess.run(
            ["git", "show", f"HEAD:{path.as_posix()}"], capture_output=True, check=False
        ).stdout
        if not committed:
            print(f"{path.name}: not in the last commit")
            continue
        old = image.imread(io.BytesIO(committed))
        new = image.imread(path)
        if old.shape != new.shape:
            print(f"{path.name}: size differs, committed {old.shape}, drawn here {new.shape}")
            continue
        difference = abs(old.astype(float) - new.astype(float))
        changed = (difference.max(axis=2) > 0).sum()
        total = difference.shape[0] * difference.shape[1]
        print(
            f"{path.name}: {changed} of {total} pixels differ ({changed / total:.4%}); "
            f"largest difference {difference.max() * 255:.0f} of 255; "
            f"pixels differing by more than 16: {(difference.max(axis=2) > 16 / 255).sum()}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
