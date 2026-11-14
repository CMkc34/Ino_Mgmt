# Source snapshots

The sub-folder `medtech/` holds the snapshots of the second scan (AI in medical technology), in the same format.

Dated copies of the source data, written by `python -m pipelines run all --refresh`.
The pipeline reads the newest one by default. See `pipelines/ingest.py` for the format.

| File prefix | Content |
|---|---|
| `publication_counts_` | Main counts: field baseline and ten sub-topics |
| `robustness_no_ai_counts_` | Robustness test D: the same without any AI condition |
| `robustness_articles_counts_` | Robustness test C: works of type "article" only |
| `discovery_topics_` | Discovery step: the source's topic labels within the field, for the first and last year of the growth window. An empty cell means the topic was not among the 200 most frequent in that year |

Each snapshot has a companion `.meta.json` note with the source, the fetch date and the exact queries used.
