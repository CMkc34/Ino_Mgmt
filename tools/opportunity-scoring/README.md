# Opportunity scoring model

Ranks a list of opportunities for one organisation on weighted criteria, tests how far the ranking depends on the weights and on uncertain scores, and sorts each opportunity into **pursue**, **explore** or **park** by a rule fixed in advance.

**Status:** the model is built and tested. It currently runs on a made-up [example set](example/). The worked example for the reference organisation, with its results and recommendation, follows.

## How it works

1. Each opportunity gets a score from 1 to 5 on five criteria, each with a one-sentence justification and a pointer to evidence.
2. The total is the weighted sum of the scores.
3. The ranking is recomputed 1,000 times with randomly varied weights, to see how often each opportunity stays in the top three.
4. Each score that rests on an assumption is moved by one point, to see whether the result changes.
5. The classification rule is applied: pursue needs a stable top-three place, a total of at least 3.5 and no score of 1.
6. For the top opportunities, a simple business case gives the payback in three cases and the break-even point.

The full method, with the reasons for each choice and its limits, is in the [method note](../../docs/design/scoring-model-method.md).

## Use it with your own opportunities

1. Copy the [`example/`](example/) folder and give it a new name.
2. Fill in `opportunities.csv` and `scores.csv` (and `business-case.csv` if you want the cost-benefit view). The model stops with a clear message if a score is missing, out of range or has no justification or evidence.
3. In [`config.yaml`](../../config.yaml), set `scoring.input_dir` to your folder, adjust the weights if needed, and change `scoring.data_label`.
4. Run `python -m pipelines run scoring`.

No code changes are needed. Results are written to [`data/processed/`](../../data/processed/) and two charts to [`outputs/figures/`](../../outputs/figures/).

## Input format

| File | Columns |
|---|---|
| `opportunities.csv` | `id`, `name`, `subtopic_id`, `use` (internal or offering), `description` |
| `scores.csv` | `opportunity_id`, `criterion`, `score` (1 to 5), `justification`, `evidence`. Evidence that starts with the word "assumption" marks the score as uncertain |
| `business-case.csv` | `opportunity_id`, `kind` (investment, running_cost or benefit), `item`, `low`, `base`, `high`, `unit`, `unit_value`, `source`. For a benefit, low/base/high is a quantity per year and `unit_value` is what one unit is worth |
