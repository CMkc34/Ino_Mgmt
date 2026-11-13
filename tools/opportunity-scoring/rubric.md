# Scoring rubric

Each opportunity gets a score from 1 to 5 on five criteria. Levels 1, 3 and 5 are described; 2 and 4 lie between them. **5 is always good**, also for risk. Weights are in [`config.yaml`](../../config.yaml).

The rubric was fixed in the [method note](../../docs/design/scoring-model-method.md) before any opportunity was scored.

## Market attractiveness (weight 0.25)

*How much value is at stake for the reference organisation if this works?* New revenue for an offering; cost saved or capacity gained for internal use.

| Score | Meaning |
|---|---|
| 1 | Under EUR 0.5 million a year, or no identifiable paying customer or cost block |
| 3 | EUR 1 to 3 million a year; demand or cost block is evident but not growing strongly |
| 5 | Over EUR 5 million a year, with evidence from market sources that demand is growing |

The thresholds are roughly 0.1%, 0.5% and over 1% of the organisation's revenue. Every value estimate is built from drivers (quantity × value) and recorded as the evidence. Growth in the trend scan is **not** evidence here: every shortlisted area passed that test already.

## Technical feasibility (weight 0.25)

*Can it be built and run with technology that exists and data the organisation can get?*

| Score | Meaning |
|---|---|
| 1 | Research stage: no commercial solutions; needs data the organisation cannot easily get |
| 3 | Proven in pilots elsewhere; commercial components exist but need substantial adaptation and data preparation |
| 5 | Standard solutions on the market; the needed data already exists in usable form |

## Strategic fit (weight 0.20)

*Does it advance the three strategy goals and build on existing strengths?*

| Score | Meaning |
|---|---|
| 1 | Advances none of the three goals |
| 3 | Clearly advances one goal |
| 5 | Advances two or more goals **and** builds on a listed strength such as the installed base |

## Time to value (weight 0.15)

*How long until the first measurable benefit, from the decision to start?*

| Score | Meaning |
|---|---|
| 1 | More than 36 months |
| 2 | 24 to 36 months |
| 3 | 12 to 24 months |
| 4 | 6 to 12 months |
| 5 | Under 6 months |

## Risk (weight 0.15; 5 = low risk)

*What can go wrong apart from the technology itself?* Regulation and liability, dependence on single suppliers, acceptance by customers or staff, and whether the step can be reversed.

| Score | Meaning |
|---|---|
| 1 | Safety-relevant or strongly regulated use, or the outcome depends on one supplier or on customer data that may be refused; hard to reverse |
| 3 | Known risks with known countermeasures; a failed pilot costs money but does no lasting damage |
| 5 | Contained, reversible, no regulatory exposure, several suppliers available |

## Keeping the criteria apart

- **Feasibility** asks only "can it be built?".
- **Time to value** asks only "how long does it take?".
- **Risk** asks only "what can go wrong that is not a technical question?".

Immature technology is scored down on feasibility, not also on risk.

## Evidence

Every score has a one-sentence justification and one of four kinds of evidence: a source from the adoption research, an external source, a fact from the [reference organisation](reference-organisation.md) (`P-…`, `S-…`), or the word "assumption" with what it rests on. A score that starts with "assumption" is treated as uncertain and tested separately.
