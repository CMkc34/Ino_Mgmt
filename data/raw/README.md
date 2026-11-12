# Source snapshots

Dated copies of the source data, written by `python -m pipelines run all --refresh`.
The pipeline reads the newest one by default. See `pipelines/ingest.py` for the format.

Each snapshot has a companion `.meta.json` note with the source, the fetch date and the exact queries used.
