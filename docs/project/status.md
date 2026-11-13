# Status

Short notes per sprint, and the record of the self-review. Newest first.

The dates show that the work ran far ahead of the charter's schedule. From 13 November the project owner asked the AI assistant to work through the remaining issues without waiting for step-by-step approval, and to review the results afterwards (requirements document, v1.5).

---

## Additions after the Must scope, from 13 November 2026

The project owner lifted the scope freeze for five items (change request CR-7).

- **Done:** Draft closure report. Three Horizons write-up, applied to the scoring results. German one-page summary. Case study on DMG MORI and the digital twin.
- **Next:** Second trend scan, on AI in medical technology.
- **Risk:** Each addition is one more draft for the owner to review.

## Sprint 3 work, done 13 November 2026

- **Done:** Self-review of the trend scan and the scoring model against every acceptance criterion (below). Cold-read test of both summaries. README with highlights, project approach and status. Automatic link check over all documents. Placeholder pages marked as planned.
- **Next:** The owner's review of both drafts and of the open decisions listed at the end of each. Presentation dry run (#17). Final acceptance and lessons learned (#19).
- **Blocked:** Nothing.
- **Risks:** The analyses, scores and texts are first drafts by the assistant. Until the owner has reviewed them and written their own reasoning (#26), the owner cannot yet be said to be able to explain and defend the work (requirement G-6, charter success criterion 6).
- **On track:** Ahead of schedule on deliverables; the owner's review is the remaining critical path.

## Sprints 1 and 2 work, done 12 to 13 November 2026

- **Done:** Search terms validated in three rounds with two raters. All data fetched. Trend metrics, robustness tests, shortlist rule and charts implemented and tested. Adoption levels researched and set. Discovery step. Draft trend scan write-up. Scoring model implemented and tested; reference case with 35 scores; draft guide with business case.
- **Changes to the plan:** The assistant wrote the data fetch (CR-5) and the analysis code (CR-6), and drafted the scores and texts, because the owner does not write Python and wanted to use a time-limited model access. The README states the division of work.
- **Problems met and solved:** The first search design failed its quality check for nine of ten sub-topics and was replaced before any counts were seen. Chart files differed between Linux and Windows although the pictures were identical; charts are now compared as pictures. A machine-specific font setting was found and neutralised.

## Sprint 0 (11 to 12 November 2026)

- **Done:** Charter, requirements and both method notes approved. Requirements research finished (14 role descriptions). Design review with seven decisions. Data source checked. Milestone M0 reached.
- **Risks named then:** hours needed above hours planned (K-1); authorship (K-5).

---

## Self-review record (13 November 2026)

Carried out by the AI assistant, which also wrote the drafts. It is therefore not independent; the owner's own review comes on top (issue #15 stays open for it).

### D1 · Data pipeline

| Criterion | Met | Evidence or note |
|---|---|---|
| AC-1.1 Fresh clone runs in five steps or fewer | Yes | README, "Running the pipeline": four commands |
| AC-1.2 No network or credentials for a normal run | Yes | Reads stored snapshots; verified on GitHub's servers without a key |
| AC-1.3 A second run changes nothing | Yes | Checked by the workflow on every pull request |
| AC-1.4 Under five minutes | Yes | A few seconds |
| AC-1.5 Tests pass; one per transform function | Yes | Two functions were only tested indirectly; direct tests added in this review |
| AC-1.6 Workflow green | Yes | Linux and Windows |
| AC-1.7 Parameters changed in the configuration only | Yes | Search terms, thresholds, weights and the scoring input folder are in `config.yaml` |
| AC-1.8 Credentials from the environment; none in the repository | Yes | `OPENALEX_API_KEY`; a search of the repository finds no key |

### D2 · Trend scan

| Criterion | Met | Evidence or note |
|---|---|---|
| AC-2.1 Summary of 150 words or fewer with question, finding, recommendation | Yes | 149 words. **Fixed in this review:** the question was missing from the summary |
| AC-2.2 8 to 12 sub-topics; queries listed or linked | Yes | Ten; filters linked from the method section |
| AC-2.3 Every number traceable to `data/processed/` | Mostly | **Fixed in this review:** yearly counts are now also written to `data/processed/trend_counts_by_year.csv`. Adoption levels and the source growth check are in `data/manual/`, not `processed/`, because they are hand-made inputs. Answered in writing here; no change planned |
| AC-2.4 Both charts made by the pipeline and embedded | Yes | |
| AC-2.5 Query-quality table present; under 70% flagged | Yes | **Fixed in this review:** the table was missing from the write-up and is now section 3.6 |
| AC-2.6 Shortlist of at most eight, each with a reason | Yes | Seven; the exception under rule 4 is marked |
| AC-2.7 Limitations cover the four required points | Yes | Limitations 1 to 4 |
| AC-2.8 External claims have sources | Yes | With the reservations recorded in `adoption.csv` |
| AC-2.9 Complete years only; fetch date stated | Yes | 2015 to 2025; 12 November 2026 |
| AC-2.10 Adoption level and source per sub-topic; shown on the trend map | Yes | |
| AC-2.11 Discovery table, with what the list missed | Yes | Three missed areas named |
| AC-2.12 Method approved before the first snapshot | Yes | Method merged in `404aac2`; first snapshot in `d5584c5` |

### D3 · Scoring model

| Criterion | Met | Evidence or note |
|---|---|---|
| AC-3.1 Summary of 150 words or fewer; ends with the recommendation | Yes | The summary ends with the recommendation; the guide has a full recommendation section |
| AC-3.2 Input list equals the shortlist | Yes | Seven areas, seven opportunities |
| AC-3.3 Rubric covers levels 1, 3 and 5 | Yes | `rubric.md` |
| AC-3.4 A test fails on a missing justification or evidence | Yes | |
| AC-3.5 A test fails if weights do not sum to 1 | Yes | |
| AC-3.6 Sensitivity results reported; fixed seed | Yes | Guide, sections 3.2 and 3.3 |
| AC-3.7 Classification follows the stated rule | Yes | Computed by the model from the rule in the configuration |
| AC-3.8 A second input set runs with a configuration change only | Yes | The example set, run by a test |
| AC-3.9 Illustrative label wherever profile and scores appear | Yes | Guide, profile, both charts |
| AC-3.10 Cost-benefit table with three cases; every input sourced or "assumption" | Yes | The model refuses an input without one |
| AC-3.11 Key figures of the organisation cite a published statistic | **Partly** | Service share and innovation spending do. No statistic on data staff in machine building was found; the figure is marked as an assumption. Answered in writing; left open |
| AC-3.12 Test of uncertain scores and near-ties reported | Yes | Guide, sections 3.1 and 3.3 |
| AC-3.13 At least five opportunities | Yes | Seven |

Also found: requirement R-3.6 asks for a reason per weight. A first draft was added to the guide for the owner to confirm or replace.

### D4 · Repository presentation

| Criterion | Met | Evidence or note |
|---|---|---|
| AC-4.1 Highlights with both charts | Yes | README |
| AC-4.2 No broken internal links | Yes | Now checked automatically by a test over every Markdown file |
| AC-4.3 Statement on AI assistance | Yes | README, "How this work was made" |
| AC-4.4 No placeholder text in delivered content | Yes | Pages for later phases are marked as planned |
| AC-4.5 Licence files present and referenced | Yes | |
| AC-4.6 Repository description and topics set on GitHub | **No** | Only the owner can set these |
| AC-4.7 Highlights link to charter, requirements and backlog | Yes | Checked by a test |

### Cold-read test

A fresh AI session with no knowledge of the project read only the two summaries and was asked for the recommendation, the main finding and the main weakness.

- It stated both recommendations and both main findings correctly.
- It rated the trend scan summary 3 of 5 and the scoring summary 4 of 5, and named real gaps: ten areas announced but nine named; the "shortlist rule" and the second signal not explained; the scale of the scores and the two parked opportunities not stated; the fictional company easy to overlook.
- **Both summaries were rewritten to close these gaps.** The rewritten versions were not tested again.

### What this review cannot settle

- Whether the scores are right. They are judgements, and so far only the assistant has made them.
- Whether the owner can present and defend the work. That is the dry run (#17).
