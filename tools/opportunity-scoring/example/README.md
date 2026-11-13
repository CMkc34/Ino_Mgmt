# Example input set

**Made-up data.** Five invented opportunities, built so that every rule of the scoring model applies once. The set is used to test the model and to show the input format. Nothing here is a finding.

| File | Content |
|---|---|
| `opportunities.csv` | One row per opportunity |
| `scores.csv` | One row per score, with a justification and evidence |
| `business-case.csv` | Optional: inputs for the cost-benefit view |

What the example shows:

| Opportunity | Total | Result | Why it is in the set |
|---|---|---|---|
| A | 4.30 | pursue | Strong all round |
| B | 4.20 | pursue | Within 0.25 of A: practically tied |
| C | 3.25 | explore | Third, but has a score of 1 on risk: the knock-out rule |
| D | 2.70 | park | Above the minimum total, but rarely in the top three |
| E | 2.25 | park | Total below the minimum |

To run the model on another set, copy this folder, fill in your own rows and point `scoring.input_dir` in `config.yaml` at it.
