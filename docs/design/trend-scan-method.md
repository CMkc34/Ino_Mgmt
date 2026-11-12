# Method design: trend scan

| | |
|---|---|
| **Deliverable** | D2 · Trend scan: AI in industrial manufacturing |
| **Version** | 0.1 |
| **Status** | Draft, awaiting the project owner's decisions (section 10) |
| **Date** | 2026-11-12 |
| **Implements** | Requirements R-2.1 to R-2.10 in [`02-requirements-and-plan.md`](../project/02-requirements-and-plan.md) |

This note fixes **how** the trend scan is done before any result is seen. Writing the method and the shortlist rule down first is deliberate: it prevents choosing, after the fact, the definitions that produce the most appealing result.

---

## 1. Question and unit of analysis

**Question:** which AI application areas in industrial manufacturing show the strongest momentum, and which deserve a closer evaluation?

**Unit of analysis:** a *sub-topic* (an application area such as predictive maintenance). Ten are defined in decision OD-2.

**What is measured:** research attention, through the number of scholarly works per year. This is a *leading, indirect* signal. It says where knowledge is being built, not where money is being made. Section 8 covers what follows from that.

## 2. Data source

| Item | Choice | Reason |
|---|---|---|
| Source | OpenAlex | Open, no licence cost, broad coverage, can count works per year for a search |
| Searched text | Title and abstract only | Full-text search also matches works that mention a term in passing, which inflates counts |
| Years | 2015 to 2025, complete calendar years | Decision OD-3. The current year is incomplete and would look like a decline |
| Work types | All types | Simple and transparent. Checked in the robustness test in section 7 |
| Access | One request per query, counts grouped by publication year | 11 requests in total |

**Known weakness of the latest year.** Indexing lags: some 2025 works are added to the source months later. This lowers the 2025 count for every query. Section 4 handles it by comparing each sub-topic with the field, which is affected in the same way.

## 3. Queries

### 3.1 Structure

Every query is built from three blocks joined with AND:

```
(sub-topic terms) AND (manufacturing context terms) AND (AI terms)
```

The **field baseline** is the same without the first block: `(context terms) AND (AI terms)`.

Reasons for this structure:

- Every sub-topic is a strict subset of the field, so "share of the field" has a clear meaning.
- The context and AI blocks are written once, so all sub-topics are measured against the same definition of "AI in manufacturing".
- A reader can see exactly what was counted.

Consequence to be aware of: a sub-topic count is *not* "all research on digital twins". It is "research on digital twins that also mentions manufacturing and an AI method in its title or abstract".

### 3.2 Draft terms

The draft terms are in [`config.yaml`](../../config.yaml). They are **untested drafts**: none has been run against the source yet.

Design rules used for the drafts:

- Phrases in double quotes, so `"digital twin"` does not match "digital" and "twin" separately.
- British and American spellings where they differ (optimisation, optimization).
- Short acronyms only where they are unambiguous in this context. `LLM` is included; `AM` (additive manufacturing) and `PdM` are not.
- No commas or pipe characters (they have a special meaning in the source's filter syntax).

Things to look at when testing the drafts:

| Sub-topic | Expected problem |
|---|---|
| Energy optimisation | Likely too broad: many works mention "energy consumption" as a side note. May need terms closer to the factory, e.g. "energy-efficient manufacturing" |
| Process optimisation and control | Broad terms; may overlap heavily with other sub-topics |
| Additive manufacturing | The context block is satisfied automatically by the word "manufacturing", so this is effectively "additive manufacturing AND AI" |
| Industrial copilots | The AI block is satisfied automatically. Very few works before 2021, so growth rates are not meaningful (section 4.4) |
| Generative design | "Topology optimisation" has a long non-AI history; the AI block should filter that, to be verified |
| Robotics and cobots | "cobot" spelling variants; check that collaborative robots are found |

### 3.3 Overlap

A work can match several sub-topics. Counts therefore do not add up to the field total, and shares do not add up to 100%. This is accepted and stated in the write-up. No attempt is made to assign each work to one sub-topic.

## 4. Metrics

Notation: `c(t)` is the number of works of a sub-topic in year `t`. `f(t)` is the same for the field.

### 4.1 Volume

```
volume = c(2023) + c(2024) + c(2025)
```

How much research there is now. Three years smooth out single-year noise.

### 4.2 Momentum

```
momentum = ( c(2025) / c(2020) ) ^ (1/5) − 1
```

The compound annual growth rate over the last five yearly steps. Chosen because it is standard, easy to explain and easy to check by hand. Its weakness is that it depends on two years only; section 7 tests whether that matters.

### 4.3 Relative momentum

```
relative momentum = momentum of the sub-topic − momentum of the field     (in percentage points)
```

This is the main ranking metric. The whole field of AI in manufacturing is growing fast, so almost every sub-topic has a high growth rate. Only growth *above* the field's says that a sub-topic is gaining attention within the field. Subtracting the field also cancels effects that hit everything equally, such as the indexing lag in 2025 and the general growth of the source.

### 4.4 Small numbers: the "emerging" flag

A growth rate from a tiny starting value is meaningless (from 2 works to 60 is a 97% yearly rate and says little).

**Rule:** if `c(2020) < 30`, momentum and relative momentum are not computed. The sub-topic is flagged **emerging** and reported with its yearly counts instead. It is shown on the charts in a separate way and discussed in words.

The threshold of 30 is a judgement: below it, a handful of works changes the rate by many points. It is a parameter in `config.yaml`.

### 4.5 Share of the field

```
share = volume of the sub-topic / volume of the field
```

Reported for context. Not used for ranking.

### 4.6 Output files

| File | Content |
|---|---|
| `data/raw/publication_counts_<date>.csv` | Yearly counts per sub-topic and for the field, as fetched |
| `data/raw/publication_counts_<date>.meta.json` | Source, fetch date and the exact queries |
| `data/processed/trend_metrics.csv` | One row per sub-topic: volume, share, momentum, relative momentum, emerging flag, results of the robustness tests |
| `data/manual/query_quality.csv` | Hand-filled result of the query-quality check (section 5) |

## 5. Query-quality check

Counts are only as good as the queries. Each query is checked by reading a sample.

**Procedure, per sub-topic:**

1. Draw 20 random works from 2023–2025 with a fixed seed: `python -m pipelines sample <sub-topic id>`.
2. Judge each from its title (open the link and read the abstract if the title is not enough).
3. A work is **relevant** if it is about applying the sub-topic in manufacturing or industrial production *and* uses an AI or data-driven method. A work that only mentions the terms in passing, or is about another sector, is not relevant.
4. Record the result in `data/manual/query_quality.csv` (columns: `subtopic_id`, `sample_size`, `relevant`, `check_date`, `comment`).
5. Under 70% relevant (fewer than 14 of 20): refine the terms and repeat, at most twice. If it is still under 70%, keep the sub-topic but flag it as unreliable and exclude it from the shortlist.

**Honest limits of this check:**

- 20 works is a small sample. An observed 70% is compatible with a true value anywhere from roughly 50% to 85%. The check catches bad queries; it does not certify good ones.
- It measures *precision* (how much of what was found is relevant). It does not measure *recall* (how much relevant work was missed). A narrow query can score 100% and still miss most of the topic. For this reason, the terms and a note on what they probably miss are published with the results.
- Changing the terms after seeing counts is allowed only in response to this check, and each change is recorded in the comment column.

## 6. Charts

Both are produced by the pipeline and follow the chart rules (G-5).

### 6.1 Time series (small multiples)

- A grid of panels, one per sub-topic, sorted by relative momentum.
- Each panel: yearly works 2015–2025 as a line with point markers.
- Each panel has its own y-axis starting at zero (the sub-topics differ too much in size for a shared axis). This is stated in the caption so heights are not compared across panels.
- The 2025 point is drawn hollow, with a caption note that the latest year is incomplete in the source.
- Emerging sub-topics carry the word "emerging" in the panel title.

### 6.2 Trend map

Called a "trend radar" in the requirements. It is a scatter plot:

- **x-axis:** volume, on a logarithmic scale (sizes differ by orders of magnitude).
- **y-axis:** relative momentum in percentage points. A horizontal line at 0 marks "growing as fast as the field".
- A vertical line at the median volume.
- Each point is labelled directly with the sub-topic name. No legend and no colour coding are needed.
- The four areas are named in the corners:

| | Smaller volume | Larger volume |
|---|---|---|
| **Above the field** | Rising niche | Growing core |
| **Below the field** | Fading or stable niche | Maturing core |

- Emerging sub-topics have no relative momentum, so they are listed in a labelled box beside the plot with their 2025 count.
- Sub-topics flagged as unreliable are drawn with a hollow marker.

## 7. Robustness tests

The ranking by relative momentum is recomputed under three alternative choices. The write-up reports whether the top five change.

| Test | Alternative | What it checks |
|---|---|---|
| A. Shifted window | Momentum from 2019 to 2024 instead of 2020 to 2025 | Dependence on the two end years and on the incomplete 2025 |
| B. Smoothed ends | Start value = average of 2019–2020, end value = average of 2024–2025 | Dependence on single-year noise |
| C. Articles only | Counts restricted to the work type "article" | Whether preprints or other types drive a trend. Needs a second fetch; done only if time allows |

A sub-topic's result is called **robust** if it stays on the same side of the field line (above or below) in tests A and B.

## 8. From results to shortlist

**Rule, fixed in advance:**

1. Candidates are all sub-topics that pass the query-quality check.
2. A candidate is shortlisted if its relative momentum is above 0 **and** robust (section 7).
3. Emerging sub-topics are shortlisted if their yearly counts rose in each of the last three years.
4. A sub-topic below the field line may be added only with a stated reason from a non-bibliographic source (for example, strong evidence of industrial adoption). The reason is written into the shortlist.
5. The shortlist has 5 to 8 items (R-2.8). If the rule yields more than 8, the lowest relative momentum is cut first. If it yields fewer than 5, the best candidates below the line are added and marked as such.

**From sub-topic to opportunity.** For the scoring model, an opportunity is a sub-topic seen from the reference organisation's viewpoint: "use X in our operations or products". A broad sub-topic may be split into two opportunities if the interpretation shows two distinct uses.

**Interpretation (R-2.7).** For each shortlisted sub-topic, 2 to 4 sentences on what drives it, with at least one source that is not a publication count: an industry survey, a standard, a vendor or adopter announcement, a market report. This is where "research attention" is checked against signs of real adoption.

## 9. Limitations to state in the write-up

Required by R-2.9, plus those that follow from this design:

1. **Publications are not adoption.** Research attention can run years ahead of industrial use, or never lead to it. Some widely adopted techniques are no longer researched much.
2. **Keyword bias.** Results depend on the chosen terms. Terminology shifts over time (a topic renamed in 2022 looks like one topic dying and another being born).
3. **Time lag.** Publications appear one to two years after the work was done, and the latest year is incomplete in the source.
4. **Source coverage.** Coverage differs by language, region and publication type. English-language works dominate. Industry work that is never published is invisible.
5. **Precision checked, recall not.** See section 5.
6. **Overlap.** Sub-topics share works.
7. **One signal.** No patents, funding or job-market data (patents are planned for Phase 2).
8. **Growth rates favour small topics.** Partly handled by the emerging flag and the volume axis, but the reader should weigh momentum and volume together.

## 10. Decisions for the project owner

| ID | Decision | Proposal |
|---|---|---|
| MD-1 | Query structure: three blocks, every sub-topic requires the AI block | As in section 3.1 |
| MD-2 | Searched text | Title and abstract only |
| MD-3 | Momentum definition | End-to-end compound growth 2020–2025 (section 4.2), with tests A and B |
| MD-4 | Relative momentum | Difference to the field in percentage points |
| MD-5 | Emerging threshold | Fewer than 30 works in 2020 |
| MD-6 | Query-quality threshold and sample | 70% of 20, at most two refinements |
| MD-7 | Shortlist rule | As in section 8 |
| MD-8 | Robustness test C (articles only) | Only if time allows |

## 11. What changes in the configuration

Once the decisions are made, these parameters are added to `config.yaml` (the first two exist already):

```yaml
trends:
  volume_window_years: 3
  growth_window_years: 5
  emerging_threshold: 30        # works in the first year of the growth window
  quality_threshold: 0.70
  quality_sample_size: 20
```
