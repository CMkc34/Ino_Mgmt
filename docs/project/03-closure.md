# 03 · Closure Report

| | |
|---|---|
| **Project** | Ino_Mgmt: applied innovation analysis |
| **Version** | 0.1 |
| **Status** | Draft, prepared early. Not yet a closure: three success criteria are still open |
| **Date** | 2026-11-13 |
| **Based on** | [Charter v1.3](01-project-charter.md), [Requirements and plan v1.6](02-requirements-and-plan.md), [Status and self-review](status.md) |

This draft was prepared by the AI assistant so that the closure only needs the project owner's review, the open points below and the sign-off. The lessons learned are a first list from the assistant's side of the work; the owner's own lessons are the part that matters and are still to be added.

---

## 1. Success criteria

From the charter, section 10.

| # | Criterion | Status | Evidence or what is missing |
|---|---|---|---|
| 1 | All Must deliverables (D0 to D4) meet their acceptance criteria | **Mostly** | 37 of the 40 criteria of D1 to D4 are fully met ([self-review](status.md)); the four of D0 were met in sprint 0. Not fully met: AC-2.3 (some figures are in `data/manual/` or `data/raw/`, not `data/processed/`), AC-3.11 (no statistic found for one profile figure) and AC-4.6 (repository description and topics, the owner's task) |
| 2 | One command reproduces every dataset and chart from a fresh clone | **Met** | `python -m pipelines run all`; checked on Linux and Windows on every pull request |
| 3 | D2 and D3 open with a summary of 150 words or fewer and end with a recommendation | **Met** | 149 and 148 words |
| 4 | Every factual claim has a source; every score traces to the rubric | **Met, with a reservation** | Sources are cited throughout. Several were found by web search without the page being opened, and several are vendors reporting on their own customers; each case is marked |
| 5 | D2 and D3 passed a documented self-review; every finding fixed or answered | **Assistant's part met** | Recorded in [`status.md`](status.md). The owner's own review is still open (#15) |
| 6 | The owner can present D2 and D3 without notes in 10 minutes, including how the code works | **Open** | Dry run not yet held (#17) |
| 7 | The owner signs off final acceptance by 8 December 2026 | **Open** | Section 6 |

**In short:** the deliverables exist and hold up against their criteria. What is open is the owner's part: reviewing, being able to explain, and accepting.

## 2. What was delivered

| ID | Deliverable | Result |
|---|---|---|
| D0 | Requirements research | 14 role descriptions analysed; led to three change requests (a cost-benefit view added, the dashboard dropped, the README to show the project approach). Kept private |
| D1 | Data pipeline | One command; stored snapshots; 153 automatic tests; checks on two operating systems |
| D2 | Trend scan | [AI in industrial manufacturing](../../trend-scans/2026-11_ai-in-industrial-manufacturing.md): ten areas, two signals, four robustness tests, a shortlist of seven |
| D3 | Opportunity scoring model | [Model, reference case and guide](../../tools/opportunity-scoring/): seven opportunities, one "pursue", four too close to rank, two parked |
| D4 | Repository presentation | README with highlights, licence, automatic link check |

## 3. What changed along the way

| Change | When | Why |
|---|---|---|
| Lead theme narrowed to one (AI in industrial manufacturing) | Charter v0.2 | Depth over breadth; one storyline |
| Power BI dashboard dropped | CR-2 | The requirements research found no demand for it |
| Cost-benefit view added | CR-1 | Budgeting was the second most requested method in the role descriptions |
| External reviewers replaced by self-review | Charter v1.0 | No reviewers available |
| Search design replaced | 12 Nov | The first design failed its quality check for nine of ten sub-topics |
| The assistant writes the code | CR-5, CR-6 | The owner does not write Python and does not aim at roles that need it |
| The assistant drafts scores and texts; the owner reviews afterwards | v1.5 | To use a time-limited model access |
| Scope freeze introduced, then lifted for five items | v1.3, CR-7 | Introduced because the hours did not fit; lifted when the Must work was drafted early |

## 4. Plan against actual

| | Planned | Actual |
|---|---|---|
| Duration | 4 weeks, to 8 December | Must deliverables drafted in 3 days (11 to 13 November) |
| Owner's hours | About 34.5 for the Must work | Not recorded. **To be estimated by the owner** |
| Who built it | The owner, with the assistant reviewing | The assistant, with the owner deciding and reviewing |
| Must deliverables | 5 | 5 drafted |
| Should / Could deliverables | 2 Should, 2 Could | Dashboard dropped; S-curve write-up not started; Three Horizons write-up and case study taken up again as additions |

The plan's hour estimates turned out to measure the wrong thing. They counted the owner's building time, and the building was done by the assistant. The real constraint became the owner's time to review and understand, which the plan did not estimate at all.

## 5. Lessons learned (first list, from the assistant's side)

### What worked

- **Fixing the method before seeing the data.** The thresholds and the shortlist rule were merged before the first fetch. When production planning missed the "emerging" threshold by one paper, there was no temptation to move the threshold, because the order of decisions was on record.
- **Checking the search before trusting the counts.** The first search design looked reasonable and was wrong: about half of what it found was irrelevant. Twenty sampled papers per topic were enough to show it.
- **A critical review before building.** It found that the classification rule could not fail and that the sensitivity test could hardly fail. Both would have produced confident-looking results from a broken method.
- **A second signal.** Adoption evidence turned "publication counts" into a finding: digital twins lead on both, copilots only on one.
- **Automatic checks on two operating systems.** They caught a chart problem that would otherwise have shown up on the owner's machine with no explanation.
- **Saying when the model cannot decide.** Four opportunities are too close to rank. Reporting that is more useful than a forced order.

### What did not work

- **Too much paperwork at the start.** Six documents were proposed for a one-person project. The design review cut this back, but two days had gone into process before any data was looked at.
- **The first scope was too big.** Seven deliverables for 24 hours. Cutting came only after a review.
- **A wrong assumption about who would build.** The plan assumed the owner would write the code. The question "can you write Python?" was not asked at the start; a broader question about background was. This shaped the whole plan and had to be reversed by two change requests.
- **Decisions by accepting proposals.** Most decisions were taken as "accept all". The design review named this as a risk, and it is still open in #26.
- **Speed traded against learning.** The fast phase produced drafts, not understanding. That was a conscious choice, but it leaves the owner's review as the largest remaining task.
- **Sources that could not be opened.** Part of the adoption evidence and the profile figures rest on search results for pages the assistant could not read. Each is marked, but it is a weaker basis than a checked source.

### What to do differently next time

- Ask about skills and available time before planning, and plan the owner's review time, not only the building time.
- Start with one small deliverable end to end, then decide the rest.
- Use a real company as the reference case, so that facts can be cited instead of assumed.
- Have a second person, not a second AI session, check a sample of the ratings and scores.
- Take each method decision with one sentence of the owner's own reasoning at the time, not afterwards.

### Still to be added by the project owner

- Your own lessons: what you learned, what surprised you, what you would not do again.
- The hours you actually spent.

## 6. Open points before closure

| # | Open point | Issue |
|---|---|---|
| 1 | Review the trend scan draft and its two open decisions | #10, #15 |
| 2 | Review the scoring guide, the 35 scores and the profile; five open decisions | #11, #13, #20 |
| 3 | Own reasoning for the method decisions; spot-check of the query ratings | #26 |
| 4 | Read the code with the self-study notes | #7 |
| 5 | Presentation dry run | #17 |
| 6 | Set the repository description and topics on GitHub | #16 |
| 7 | Decide whether AC-3.11 is accepted as it is | |

## 7. Acceptance

| Role | Decision | Date |
|---|---|---|
| Project owner | ☐ Accepted ☐ Accepted with open points ☐ Not accepted | |
