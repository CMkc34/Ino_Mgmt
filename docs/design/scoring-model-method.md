# Method design: opportunity scoring model

| | |
|---|---|
| **Deliverable** | D3 · Opportunity scoring model |
| **Version** | 0.1 |
| **Status** | Draft, awaiting the project owner's decisions (section 12) |
| **Date** | 2026-11-12 |
| **Implements** | Requirements R-3.1 to R-3.11 in [`02-requirements-and-plan.md`](../project/02-requirements-and-plan.md) |
| **Input from** | The shortlist of the trend scan ([method](trend-scan-method.md), section 8) |

Like the trend scan method, this note fixes the rules **before** any opportunity is scored: the rubric, the way scores are combined, the sensitivity check and the rule that turns numbers into a recommendation.

Everything marked *draft* is a proposal for the owner to change. The scores themselves are not in this note: the owner sets them in sprint 2.

---

## 1. The decision this model supports

*"Given a limited innovation budget, which two or three AI opportunities should this manufacturer pursue now, which should it explore with a small effort, and which should it park?"*

The model does not find the "best technology". It ranks options **for one organisation**, because fit, feasibility and risk depend on who is asking.

## 2. Reference organisation (draft, fictional)

> **Illustrative.** This company does not exist. The profile is a plausible composite, written so that scores have something concrete to refer to.

| | |
|---|---|
| **Business** | Builds special-purpose production machines and automation cells for automotive suppliers and general industry |
| **Size** | About 2,000 employees, about EUR 400 million revenue, three plants in Central Europe |
| **Ownership** | Family-owned; cautious about large, uncertain investments |
| **Revenue mix** | About 80% new machines, 20% service and spare parts |
| **Installed base** | Several thousand machines at customers, roughly a third with remote connectivity |

**Strategy (three goals).** The rubric for strategic fit refers to these.

1. **Grow service revenue** from 20% to 30% of revenue within five years.
2. **Raise operating margin** through more efficient engineering and production.
3. **Differentiate the machines** through digital functions customers will pay for.

**Capabilities and constraints.** The rubrics for feasibility and risk refer to these.

| Strengths | Weaknesses and constraints |
|---|---|
| Deep mechanical and process know-how | Data and software team of about 10 people |
| Close, long-term customer relationships | Machine data fragmented, different controller generations |
| Large installed base as a data source and service channel | Customers own their production data; access must be negotiated |
| Own production as a test bed | Budget for digital innovation about EUR 2 million a year |
| | Skilled-labour shortage in engineering and service |

Each fact above has an id in the final version (`P-1`, `P-2`, …), so a score can point to it as evidence.

## 3. What counts as an opportunity

An opportunity is a sub-topic from the trend scan **applied to a use at the reference organisation**. Each one is written in a fixed form:

| Field | Content |
|---|---|
| `id` | Short identifier |
| `name` | For example "Predictive maintenance as a service for the installed base" |
| `subtopic_id` | Link to the trend scan |
| `use` | `internal` (own engineering and production) or `offering` (product or service for customers) |
| `description` | One or two sentences: who uses it, for what, and what changes |

The `use` matters. The same technology scores differently as an internal efficiency measure than as a product for customers, so a sub-topic may appear twice.

## 4. Criteria and rubric (draft)

Five criteria, each scored from 1 to 5. Levels 1, 3 and 5 are described; 2 and 4 lie between them. **5 is always good**, also for risk.

### 4.1 Market attractiveness (weight 0.25)

*How much value is at stake for the reference organisation if this works?* For an `offering`, value means new revenue. For `internal` use, it means cost saved or capacity gained. "Market" is used in this broad sense.

| Score | Meaning |
|---|---|
| 1 | Yearly value potential under EUR 0.5 million, or no identifiable paying customer or cost block |
| 3 | EUR 1–3 million a year; demand or cost block is evident but not growing strongly |
| 5 | Over EUR 5 million a year, with evidence that demand is growing (trend scan momentum above the field, or market sources) |

### 4.2 Technical feasibility (weight 0.25)

*Can it be built and run with technology that exists and data the organisation can get?*

| Score | Meaning |
|---|---|
| 1 | Research stage: no commercial solutions; needs data the organisation does not have and cannot easily get |
| 3 | Proven in pilots elsewhere; commercial components exist but need substantial adaptation and data preparation |
| 5 | Standard solutions on the market; the needed data already exists in usable form |

### 4.3 Strategic fit (weight 0.20)

*Does it advance the three strategy goals and build on existing strengths?*

| Score | Meaning |
|---|---|
| 1 | Advances none of the three goals |
| 3 | Clearly advances one goal |
| 5 | Advances two or more goals **and** builds on a listed strength (for example the installed base) |

### 4.4 Time to value (weight 0.15)

*How long until the first measurable benefit, counted from the decision to start?*

| Score | Meaning |
|---|---|
| 1 | More than 36 months |
| 2 | 24 to 36 months |
| 3 | 12 to 24 months |
| 4 | 6 to 12 months |
| 5 | Under 6 months |

### 4.5 Risk (weight 0.15; 5 = low risk)

*What can go wrong apart from the technology itself?* Covers regulation and liability, dependence on single suppliers, customer or staff acceptance, and whether the step can be reversed.

| Score | Meaning |
|---|---|
| 1 | Safety-relevant or strongly regulated use, or the outcome depends on one supplier or on customer data that may be refused; hard to reverse |
| 3 | Known risks with known countermeasures; a failed pilot costs money but does no lasting damage |
| 5 | Contained, reversible, no regulatory exposure, several suppliers available |

### 4.6 Keeping the criteria apart

Three criteria are easy to mix up, which would count the same weakness three times:

- **Feasibility** asks only "can it be built?".
- **Time to value** asks only "how long does it take?".
- **Risk** asks only "what can go wrong that is *not* a technical question?".

A technology that is immature is scored down on feasibility, not also on risk.

### 4.7 Evidence rule

Every score is one row with five fields: `opportunity_id`, `criterion`, `score`, `justification` (one sentence) and `evidence`. Evidence must be one of:

| Type | Example |
|---|---|
| Trend scan metric | "relative momentum +6 points, `trend_metrics.csv`" |
| External source | Author or organisation, year, link |
| Profile fact | `P-4` (data team of about 10) |
| Assumption | The word "assumption", plus what it rests on |

A score backed only by an assumption is allowed, but it is visible as such, and section 7.4 tests how much such scores matter.

## 5. Combining the scores

```
total score of an opportunity = sum over criteria of ( weight × score )
```

A weighted sum, giving a value between 1 and 5. Chosen because it is transparent and can be checked by hand. More elaborate methods exist; they would add machinery without adding evidence.

**Weakness, and the rule that handles it.** In a weighted sum, a very bad score can be offset by good ones. An opportunity with a 1 on risk could still rank first. Therefore:

> **Knock-out rule:** an opportunity with a score of 1 on any criterion cannot be classified as "pursue", whatever its total.

## 6. Weights

Starting weights are those of decision OD-5 (shown in section 4). The owner confirms or changes them **before** scoring and writes one sentence of reasoning per weight, from the reference organisation's situation (for example: a cautious, family-owned company might weight risk higher).

Weights are never tuned after the ranking is known. The sensitivity check exists to show what other weights would do.

## 7. Sensitivity check

Scores and weights are judgements. The check answers: *would a reasonable person with somewhat different views reach a different recommendation?*

### 7.1 Random weights

1. Take the base weights.
2. Change each one by a random factor between 0.5 and 1.5 (each weight can be up to 50% lower or higher).
3. Rescale the five weights so they sum to 1 again.
4. Recompute the ranking.
5. Repeat 1,000 times with a fixed random seed (42), so the result is identical on every run.

This models *reasonable disagreement* about the weights, not arbitrary weights.

### 7.2 Top-3 share

For each opportunity: in what share of the 1,000 runs is it among the top three? This is the main stability measure and feeds the classification in section 8.

### 7.3 Swap point for ranks 1 and 2

For each criterion in turn: raise or lower its weight in steps of 0.01 from 0 to 1, rescaling the other four in proportion, and note the first weight at which ranks 1 and 2 swap. Report the criterion with the smallest change needed, for example: *"A overtakes B if the weight of risk rises from 0.15 to 0.27."* If no weight between 0 and 1 produces a swap, rank 1 is said to be *dominant*.

### 7.4 Uncertain scores (only if time allows)

Each score that rests on an assumption is moved by one point up and down, one at a time, and the ranking is recomputed. Report which single score changes, if any, alter the top three. This tests the scores, where 7.1 to 7.3 test the weights.

## 8. From numbers to a recommendation

The rule is fixed in advance:

| Class | Rule |
|---|---|
| **Pursue** | In the top three in at least 70% of runs, **and** no score of 1 |
| **Park** | In the top three in fewer than 20% of runs, **or** total score below 2.5 |
| **Explore** | Everything else |

"Explore" means a small, time-limited step to resolve the main uncertainty (named in the recommendation), not a general "maybe".

The recommendation states, for each class, what the organisation should do next and what would change the classification.

## 9. Charts

Both follow the chart rules (G-5) and are produced by the pipeline.

**9.1 Rank stability.** Horizontal bars, one per opportunity, sorted by total score. Bar length is the top-3 share. Vertical lines at 70% and 20% mark the class boundaries. Each bar is labelled with the opportunity name and its total score.

**9.2 Score against time horizon.** A scatter plot: x-axis is time to first value in months (the midpoint of the band from section 4.4), y-axis is the total score. Points are labelled directly. Three shaded bands mark the horizons: under 12 months, 12 to 36 months, over 36 months. The caption notes that the Three Horizons framework is about more than time; the framework write-up (D5) covers that.

## 10. Cost-benefit view for the top two (R-3.11)

A rough business case, to test whether the two top-ranked opportunities also make financial sense. It is illustrative, since the organisation is fictional. Its value is the structure of the reasoning, with every input visible.

### 10.1 Structure

| Block | Items |
|---|---|
| **One-off investment** | Software and licences; integration and engineering; data preparation; hardware (sensors, computing); training; own staff time at an internal day rate |
| **Yearly running cost** | Licences and cloud; maintenance of the model and data pipelines; support staff |
| **Yearly benefit** | Built from **drivers**, never a single guessed number (see below) |

**Benefit drivers.** A benefit is always quantity × value, for example:

- avoided downtime hours × cost of a downtime hour;
- reduction in scrap rate × yearly material cost;
- engineering hours saved × hourly cost;
- service contracts sold × yearly price × margin.

### 10.2 Calculation

```
yearly net benefit = yearly benefit − yearly running cost
payback period     = one-off investment / yearly net benefit
```

Simple payback, without discounting. It is the measure most readers know and can check in their heads. If the yearly net benefit is zero or negative, the result is reported as "no payback".

### 10.3 Three cases

| Case | Rule |
|---|---|
| Cautious | Investment at the upper end of its range, benefit drivers at the lower end |
| Base | Midpoints |
| Optimistic | Investment at the lower end, benefit drivers at the upper end |

### 10.4 Inputs table

Every input is a row: item, low, base, high, unit, and either a source or the word "assumption". The base-case result is compared with at least one published benchmark for a similar project. If they differ by more than a factor of two, the difference is explained.

### 10.5 Link back to the ranking

The recommendation says whether the business case supports or weakens each classification. A top-ranked opportunity with no payback in the cautious case is still presented, with that tension stated openly.

## 11. Files

| File | Content | Maintained |
|---|---|---|
| `tools/opportunity-scoring/README.md` | Guide, results and recommendation | By hand |
| `tools/opportunity-scoring/reference-organisation.md` | The profile, with fact ids | By hand |
| `tools/opportunity-scoring/rubric.md` | The rubric from section 4 | By hand |
| `tools/opportunity-scoring/opportunities.csv` | One row per opportunity (section 3) | By hand |
| `tools/opportunity-scoring/scores.csv` | One row per score (section 4.7) | By hand |
| `tools/opportunity-scoring/business-case.csv` | Inputs table (section 10.4) | By hand |
| `data/processed/scoring_ranking.csv` | Total score and rank per opportunity | Pipeline |
| `data/processed/scoring_sensitivity.csv` | Top-3 share, class and swap points | Pipeline |
| `outputs/figures/scoring_*.png` | The two charts | Pipeline |

Tests required by the acceptance criteria: weights sum to 1 (AC-3.5); every score has a justification and evidence (AC-3.4); scores are whole numbers from 1 to 5; every opportunity has a score for every criterion; a second, made-up input set runs without code changes (AC-3.8).

## 12. Limitations to state in the guide

1. **Scores are judgements by one person.** In practice a panel would score independently and discuss differences. The sensitivity check is a partial substitute.
2. **The organisation is fictional.** The ranking is valid for the profile, not for any real company.
3. **A weighted sum lets strengths offset weaknesses.** The knock-out rule limits this but does not remove it.
4. **Scores of 1 to 5 are treated as if the steps were equal.** A 4 is not exactly "twice as good" as a 2.
5. **Criteria are not fully independent**, despite section 4.6. Immature technology tends to mean slower and riskier.
6. **The business case is a rough range**, not a forecast. Simple payback ignores the time value of money and benefits after the payback point.
7. **The input list comes from one signal** (publication trends). Opportunities invisible in research are missing.

## 13. Decisions for the project owner

| ID | Decision | Proposal |
|---|---|---|
| SD-1 | Reference organisation profile | As drafted in section 2; the owner adjusts it to their own engineering experience |
| SD-2 | Rubric wording and the money thresholds for market attractiveness | As drafted in section 4 |
| SD-3 | Knock-out rule | Adopt (section 5) |
| SD-4 | Range of the random weights | Each weight varied by up to ±50% |
| SD-5 | Class thresholds | Pursue from 70%, park under 20% or total under 2.5 |
| SD-6 | Test of uncertain scores (section 7.4) | Only if time allows |
| SD-7 | Business case measure | Simple payback in three cases |
| SD-8 | Weights | Keep the starting weights of OD-5 unless the owner's reasoning for the profile says otherwise |
