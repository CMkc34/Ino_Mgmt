"""Folder locations used by every pipeline step.

All paths are built from the repository root, so the pipeline works no
matter which folder it is started from, and on any operating system.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILE = REPO_ROOT / "config.yaml"
RAW_DIR = REPO_ROOT / "data" / "raw"              # source snapshots
MANUAL_DIR = REPO_ROOT / "data" / "manual"        # files filled in by hand
PROCESSED_DIR = REPO_ROOT / "data" / "processed"  # analysis-ready CSV files
FIGURES_DIR = REPO_ROOT / "outputs" / "figures"   # charts
SCORING_DIR = REPO_ROOT / "tools" / "opportunity-scoring"


def in_repo(relative_path: str) -> Path:
    """Turn a path written in config.yaml (relative to the repository) into a full path."""
    return REPO_ROOT / relative_path
