# Hand-maintained data: second trend scan (AI in medical technology)

The same files as for the first scan, one folder up, for the second scan. See [the README there](../README.md) for what each file is.

| File | Content |
|---|---|
| `query_quality.csv` | Result of each round of the query-quality check, per sub-topic and rater |
| `query_quality_ratings.csv` | The 200 works rated in the final round, by both raters |
| `adoption.csv` | Adoption level (0 to 3) per sub-topic with source, check date and comment |
| `discovery_mapping.csv` | For each of the fifteen fastest-growing topic labels: the sub-topic it corresponds to, or \"none\" |

## How this scan's inputs were made

Everything in this folder was produced by the AI assistant on 14 November 2026, while working through the remaining issues at the project owner's request. Nothing here has been checked by the owner yet.

**Query-quality check.** Three rounds. The first field definition used the bare words \"diagnosis\", \"pathology\" and \"wearable\"; they also matched machine fault diagnosis, plant pathology and, through the word stem \"wear\", machining papers on tool wear. The field was narrowed to clinical and device terms. Two raters, both sessions of the same AI model, rated the final samples from titles only: they agree on 189 of 200 works (94.5%, Cohen's kappa 0.78). All ten sub-topics reach the 70% threshold on the lower of the two ratings; language models in medicine is exactly on it.

**Adoption levels.** The scale is the one of the first scan. The rule for level 3 was carried over by the assistant, with care providers in place of manufacturers: a survey in which at least 25% of hospitals or clinicians say they use the technology. For level 1, an authorisation by a medicines and devices regulator counts as a product on offer. **This adaptation has not been decided by the owner.** Three rows (ophthalmic imaging, endoscopy, wearables) cite a regulatory authorisation from the assistant's memory, because the search found no source; they are marked in the comment column and must be checked before use.
