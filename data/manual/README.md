# Hand-maintained data

Files here are filled in by hand and read by the pipeline. Each file is described in the design note that defines it.

| File | Content | Defined in |
|---|---|---|
| `query_quality.csv` | Result of each round of the query-quality check, per sub-topic | [Trend scan method](../../docs/design/trend-scan-method.md), section 5 |
| `adoption.csv` | Adoption level (0 to 3) per sub-topic with its source. To be filled in by the owner | [Trend scan method](../../docs/design/trend-scan-method.md), section 6.3 |
| `source_growth_check_2026-11-12.csv` | A one-off check of how the whole source grew per year, to judge the jump in 2025. Each row has its filter, so it can be repeated. Findings below | Trend scan method, section 2 (latest year) |
| `query_quality_ratings.csv` | The 200 works rated in the final round, with the reason for each "not relevant" | Same |

The ratings so far are a first pass by the AI assistant (column `rater`). The owner's spot-check is added as further rows.

## Findings of the source growth check (2026-11-12)

The field baseline grew 53% from 2024 to 2025. The check asked whether that is an effect of the source.

| What is counted | Growth 2024 to 2025 |
|---|---|
| All works in the source (six counted types) | +16% |
| All preprints in the source | +53% |
| Works with manufacturing terms | +11% |
| Works with AI terms | +45% |
| Field baseline (both) | +53% |
| Control: "heat exchanger" in the title | +2% |
| Control: "welding" in the title | +3% |

Reading:

- **The latest year is not under-counted.** The source as a whole grew 16% in 2025, after years of little change. The expected dip from indexing lag is not visible.
- **The jump in the field follows the AI terms**, which grew 45% across all subjects, while classic engineering topics hardly moved. It is mostly not an effect of the source growing.
- **Part of it is new repository content.** Preprints rose by half across the source, and two repositories (SSRN, Zenodo) contribute visibly more field works in 2025 than in 2024. Within the field, works of type "article" alone still grew 57%, so the jump does not depend on preprints.
- **What the counts cannot tell:** whether there is more AI research, or more papers that mention AI in their abstract.

For the write-up: state this next to the 2025 figures, and treat robustness test A (2019 to 2024) and test C (articles only) as the checks on it.
