# Hand-maintained data

Files here are filled in by hand and read by the pipeline. Each file is described in the design note that defines it.

| File | Content | Defined in |
|---|---|---|
| `query_quality.csv` | Result of each round of the query-quality check, per sub-topic | [Trend scan method](../../docs/design/trend-scan-method.md), section 5 |
| `adoption.csv` | Adoption level (0 to 3) per sub-topic with its source, the date checked and a comment. Rules and status below | [Trend scan method](../../docs/design/trend-scan-method.md), section 6.3 |
| `source_growth_check_2026-11-12.csv` | A one-off check of how the whole source grew per year, to judge the jump in 2025. Each row has its filter, so it can be repeated. Findings below | Trend scan method, section 2 (latest year) |
| `query_quality_ratings.csv` | The 200 works rated in the final round, with the reason for each "not relevant" | Same |

The ratings so far come from two AI sessions (column `rater`). The owner's spot-check is added as further rows.

## Second rating of the query-quality sample (2026-11-12)

A separate AI session rated the same 200 works without seeing the first ratings, using the rule in the method note.

| | |
|---|---|
| Same rating on | 192 of 200 works (96%) |
| Agreement beyond chance (Cohen's kappa) | 0.82 |
| Rated relevant by the first / second rater | 175 / 173 |
| Disagreements | 8, all marked "unsure" by the second rater |

Counting a work as relevant only when **both** raters say so, every sub-topic still reaches the 70% threshold. Three are exactly on it: digital twins, energy optimisation and industrial copilots (14 of 20 each).

Limits:

- Both raters are sessions of the same AI model, so they may share blind spots. This is weaker evidence than a second human rater.
- The second rater marked 57 of the 200 ratings as close calls. The rule leaves room for judgement, mostly on whether an AI method is really used and where "manufacturing" ends.
- The owner's spot-check is still open. The eight disagreements are the best place to start: filter the ratings file for rows where the two `relevant` columns differ.

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

## Adoption levels (2026-11-13)

The scale is defined in the trend scan method, section 6.3. Two rules were set by the project owner before the levels were assigned, because the method note left them open:

- **Level 3 ("widespread")** needs a survey in which at least 25% of manufacturers say they use the technology in operation. Piloting and planning do not count. A share of equipment installed is not a survey of manufacturers.
- **What is rated** is the application area in industrial use. Most sources do not separate AI-based use from other use; the comment column says for each row whether the source is specific to AI. The adoption signal is therefore broader than the publication counts, which require an AI method.

How the levels were set: the AI assistant searched for sources and opened the pages it could reach; the owner checked the sources for the first three sub-topics, set the two rules and decided all ten levels. The comment column records for each row who checked the page.

Open points:

- **Process optimisation and energy optimisation rest on one and the same case**: the AI kiln control at Heidelberg Materials' Mokra cement plant. The figures are from its first month of operation, and the reports were found by search without the assistant opening the pages. A second case outside the cement industry would strengthen both.
- **Industrial copilots** stay at level 1: products are on offer, but only pilots and planned rollouts were found, not confirmed use in production.
- **Several sources are not independent**: suppliers and vendors reporting on their own customers or markets. The comments say where.
- **Evidence ages quickly.** Each row carries the date it was checked.
