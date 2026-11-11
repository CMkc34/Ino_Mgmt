"""Loads config.yaml."""

from pathlib import Path

import yaml

from pipelines.paths import CONFIG_FILE


def load_config(path: Path = CONFIG_FILE) -> dict:
    """Return the configuration file as a nested dictionary."""
    with open(path, encoding="utf-8") as file:
        return yaml.safe_load(file)
