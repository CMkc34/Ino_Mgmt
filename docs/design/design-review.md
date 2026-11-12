# Design review

| | |
|---|---|
| **Reviewed** | Project plan, [trend scan method](trend-scan-method.md) v0.1, [scoring model method](scoring-model-method.md) v0.1 |
| **Date** | 2026-11-12 |
| **Viewpoint** | A sceptical reader who has to decide whether to trust the results |
| **Status** | Closed. All proposals accepted by the project owner on 2026-11-12 (section 4) |

The review was done before any data was fetched or any opportunity scored, when changes are cheapest.

**Limit of this review.** It was written by the same assistant that drafted the two methods, so it is not independent. Finding 6 addresses that.

Severity: **High** = can invalidate a conclusion or the credibility of the work. **Medium** = weakens a result. **Low** = worth stating.

---

## 1. Findings on the overall approach

### 1 · High · Publication counts are a long way from business opportunities

The trend scan measures academic attention. The scoring model then treats the result as a list of opportunities for a machine builder. A sceptic asks: *why should a manufacturer care how many papers were written?* Academic output follows funding and fashion, and some widely used techniques are barely researched any more.

**Response proposed:** add a second, independent signal. For each of the ten sub-topics, the owner records an **adoption level** from non-academic sources, on a fixed scale (for example: 0 = no commercial offer found; 1 = vendors offer it; 2 = documented deployments at named manufacturers; 3 = reported as widespread in an industry survey), with the source. The trend map can then show research momentum against adoption. This turns the weakest point into a strength: "rising in research but not yet adopted" is exactly what a scout looks for. Cost: about 1 hour. *Owner decision D-1.*

### 2 · High · The scan can only rank what was put into it

The ten sub-topics were chosen in advance. The scan cannot discover an area nobody thought of, yet discovery is the core of trend scouting.

**Response proposed:** one exploratory step. Within the field baseline, ask the source which of its own topic labels grew fastest between 2020 and 2025, and compare the top 15 with the ten sub-topics. Report what the list missed in a short table, and say whether anything is added. Cost: about 1 hour including code. *Owner decision D-2.*

### 3 · High · The ranking rests on one person's scores for a fictional company

Scores, weights and the company are all chosen by the author. The result can look like an opinion with decimals. A sensitivity check on weights does not answer this, because the judgement sits mainly in the scores.

**Responses:**
- *Fixed in v0.2:* the test of uncertain scores is now required, and near-ties are reported as ties.
- *Proposed:* present D3 as **a reusable method with a worked example**, not as a finding about the world. The guide's summary should say so in its first sentence.
- *Option:* anchor the profile's figures (service share, size of the data team, innovation budget) in cited industry statistics, so the fictional company is at least a documented typical one. A real company as the reference would be stronger still, but costs research time and is better placed in the Phase 2 case study. *Owner decision D-3.*

### 4 · High · It is hard to see what the owner contributed

So far the commit history contains only assistant commits: the project documents, both method designs, the rubric draft and the data fetch. The owner has made the decisions, but mostly by accepting proposals. Anyone who opens the history will see this.

**Response proposed:**
- For each of the method decisions (MD-1 to MD-9, SD-1 to SD-8), the owner writes **one sentence of their own reasoning**, including where they disagree. "Accept all" is the answer a sceptic is looking for.
- The owner rewrites the reference organisation in their own words, from their engineering experience.
- The execution (transform code, charts, quality check, scores, write-ups) is committed by the owner.
- The README states the division of work precisely.

*Owner decision D-4.*

### 5 · High · Much process, no analysis yet, and the hours do not fit

Four merged pull requests of documents and zero results. The Must work is estimated at 30.5 hours against a stated 24, sprint 0 is nearly over, and the fixes in this review add about 3 hours. The risk named in the charter ("too much time on paperwork") has materialised.

**Response proposed:**
- No further project documents. The two method notes are frozen once the decisions are made.
- From now on, change requests may only *remove* scope, unless something is broken.
- Cut list, decided now and applied in this order when a sprint overruns: (1) case study D6, (2) Three Horizons write-up D5, (3) robustness test C, (4) business case for the second opportunity (keep one).
- Consider moving D5 and D6 to Phase 2 today, which pays for findings 1 and 2.

*Owner decision D-5.*

### 6 · Medium · Nobody independent checks the work

The self-review is done by the author, and the assistant review by the same assistant that designed the method.

**Response proposed:** a cold-read test. Give only the 150-word summary of each analysis to someone who has not seen the project (a fellow student, or a fresh AI session with no context) and ask them to state the recommendation and the main weakness. If they cannot, the summary is rewritten. Cost: 20 minutes. *Owner decision D-6.*

### 7 · Medium · D3 has no input if D2 slips

The scoring model depends entirely on the shortlist.

**Response proposed:** build and test the scoring code first on the made-up input set that AC-3.8 already requires. The code is then ready when the shortlist arrives. No extra cost; a change of order within sprint 2.

---

## 2. Findings on the trend scan method

### 8 · High · Requiring AI terms distorts the comparison between sub-topics

*Fixed in v0.2.* Each query required words such as "machine learning" in the title or abstract. Many applied papers name the method ("random forest") and never use the general term, and how often they do differs by sub-topic and changes over the years. The ranking could then reflect wording habits.

**Response:** the AI block now includes common method names, and robustness test D recomputes the ranking without the AI block. A sub-topic that changes sides in test D is discussed as a possible wording effect.

### 9 · Medium · Two sub-topics satisfy a query block automatically

"Additive manufacturing" always satisfies the manufacturing block, and "industrial copilots" always satisfies the AI block, so these two are defined more loosely than the other eight. The copilot terms also sit inside the field definition, so that sub-topic lifts the baseline it is compared with.

**Response proposed:** state this in the write-up next to both results. No change to the method.

### 10 · Medium · The base year 2020 was not a normal year

Publication patterns in 2020 and 2021 were unusual, and momentum is computed from 2020.

**Response:** already covered by robustness tests A and B. The write-up should mention the reason.

### 11 · Medium · The shortlist rule has an escape hatch and may force padding

Rule 4 lets a sub-topic below the field line onto the shortlist "with a stated reason", and rule 5 fills the list up to five. Both weaken the claim that the rule was fixed in advance.

**Response proposed:** rule 4 may be used at most once, and the write-up marks that item. Rule 5 is changed so that the list is not padded: if fewer than five sub-topics qualify, the list stays short, and the scoring model gets its five or more opportunities by splitting sub-topics into internal use and offering. This needs a small change to R-2.8 and AC-2.6. *Owner decision D-7.*

### 12 · Low · Thresholds are judgements

The emerging threshold (30 works) and the quality threshold (70% of 20) are reasonable but not derived. The method note says so. The owner should be able to say why in one sentence each (see finding 4).

### 13 · Medium · "Fixed before the results" must be provable

The method claims to be set before the data is seen, but the first fetch was about to happen before the decisions were recorded.

**Response:** *fixed in v0.2.* The decisions are merged before the first snapshot is committed, so the Git history proves the order.

---

## 3. Findings on the scoring model method

### 14 · High · With a short list, "pursue" was guaranteed

*Fixed in v0.2.* The rule was "in the top three in 70% of runs". With five or six opportunities, about three of them meet that whatever their quality. The model could not return "nothing is good enough".

**Response:** pursue now also needs a total of at least 3.5.

### 15 · High · The sensitivity check could hardly fail

*Fixed in v0.2.* The base weights are close together (0.15 to 0.25). Changing each by half and rescaling rarely reorders anything, so the check would have reported "stable" almost regardless of the data.

**Response:** a second test with freely drawn weights is reported alongside; the test of uncertain scores is required; totals within 0.25 are called practically tied.

### 16 · Medium · One chart plotted time against itself

*Fixed in v0.2.* The time-horizon chart had time to value on the x-axis and the total score, which includes time to value, on the y-axis.

**Response:** the y-axis now uses the other four criteria only.

### 17 · Medium · The trend result was used twice

*Fixed in v0.2.* Momentum above the field puts a sub-topic on the shortlist, and the rubric also rewarded it under market attractiveness. Every shortlisted item would have received the bonus.

**Response:** removed from the rubric. Market attractiveness now needs market evidence and a driver-based estimate.

### 18 · Medium · The value thresholds are invented numbers

Market attractiveness carries a quarter of the weight and rests on euro estimates for a company that does not exist.

**Response:** partly addressed in v0.2 (thresholds tied to revenue share; estimates built from drivers). It remains the least evidence-based criterion, and the guide should say so. Finding 3's option of documented profile figures would help most here.

### 19 · Medium · A payback figure for a fictional company is false precision

**Response:** *fixed in v0.2* by adding a break-even view: what the main benefit driver would have to reach for payback within three years, compared with published benchmarks.

### 20 · Low · Rubric details

- Strategic fit can reach 5 too easily: anything that touches service and the installed base qualifies. The owner should check, after scoring, whether the criterion separates the opportunities at all. If every item gets 4 or 5, the rubric is tightened and the change recorded.
- Risk bundles four different risks into one number. The justification sentence should name which one drove the score.

---

## 4. Decisions by the project owner

All seven proposals were accepted on 2026-11-12. They are carried out in the method notes (v1.0), the requirements document (v1.3) and the charter (v1.2). D-4 is an action for the owner and stays open until done.

| ID | Finding | Decision needed | Proposal | Hours |
|---|---|---|---|---|
| D-1 | 1 | Add an adoption level per sub-topic as a second signal? | Yes | +1 |
| D-2 | 2 | Add one exploratory discovery step? | Yes | +1 |
| D-3 | 3 | Fictional company as drafted, fictional with cited typical figures, or a real company? | Fictional with cited typical figures; real company in Phase 2 | +0.5 |
| D-4 | 4 | Write own one-sentence reasoning per method decision, and rewrite the profile in own words? | Yes | +1 |
| D-5 | 5 | Freeze documents, adopt the cut list, and move D5 and D6 to Phase 2 now? | Yes to all three | −7 from the Should work |
| D-6 | 6 | Cold-read test of both summaries? | Yes | +0.3 |
| D-7 | 11 | Limit the escape hatch and stop padding the shortlist? | Yes | 0 |

Already fixed in the method notes (v0.2), for information: findings 8, 13, 14, 15, 16, 17, 19. The required test of uncertain scores (finding 15) adds about 0.5 hours to sprint 2.

**Effect on the plan if all proposals are accepted:** the Must work rises from about 30.5 to about 34.5 hours. Moving D5 and D6 to Phase 2 removes the 7 hours of Should work that were unlikely to happen anyway, but does not reduce the Must hours. The honest reading is that the Must scope needs either about 8.5 hours a week for the remaining four weeks, or a later end date.
