# Hand-maintained data

Files here are filled in by hand and read by the pipeline. Each file is described in the design note that defines it.

| File | Content | Defined in |
|---|---|---|
| `query_quality.csv` | Result of each round of the query-quality check, per sub-topic | [Trend scan method](../../docs/design/trend-scan-method.md), section 5 |
| `query_quality_ratings.csv` | The 200 works rated in the final round, with the reason for each "not relevant" | Same |

The ratings so far are a first pass by the AI assistant (column `rater`). The owner's spot-check is added as further rows.
