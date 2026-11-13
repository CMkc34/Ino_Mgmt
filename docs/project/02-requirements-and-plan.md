# 02 · Requirements and Plan

| | |
|---|---|
| **Project** | Ino_Mgmt: applied innovation analysis |
| **Version** | 1.4 |
| **Status** | Approved |
| **Date** | 2026-11-13 |
| **Based on** | [Project charter v1.2](01-project-charter.md) |

### Change history

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-11-11 | First draft |
| 1.0 | 2026-11-11 | Approved by the project owner. All proposals for the open decisions accepted (section 9). Plan updated for OD-7: pipeline scaffolding supplied by the assistant, skeleton moved to sprint 0 |
| 1.1 | 2026-11-12 | Changes approved by the project owner after the requirements research (D0). CR-1: cost-benefit view added to D3 (R-3.11, AC-3.10; +1.5 h). CR-2: portfolio dashboard (D7) moved to Phase 2. CR-3: README highlights how the project was run (R-4.7, AC-4.7; +0.5 h). CR-4 (slide deck from the dry run): rejected for this phase. R-0.2 and AC-0.1 changed: the research covers corporate and public-sector employers; consultancies are not covered |
| 1.2 | 2026-11-12 | CR-5, requested by the project owner: the assistant writes the reference implementation of the data fetch (`pipelines/openalex.py` and the fetch in `pipelines/ingest.py`), as a stated exception to G-7. G-6 still applies: the owner reviews and annotates the code and must be able to explain it before D1 is accepted. Design work for D2 is moved forward into sprint 0 ([method design note](../design/trend-scan-method.md)). Sprint 1 estimate for ingest and transform reduced from 2.5 h to 1.5 h |
| 1.3 | 2026-11-12 | Method decisions MD-1 to MD-9 and SD-1 to SD-8 and review decisions D-1 to D-7 approved by the project owner. Added: adoption level (R-2.11), discovery step (R-2.12), proof of order (AC-2.12), cited profile figures (AC-3.11), test of uncertain scores (AC-3.12), cold-read test. Changed: shortlist rule (R-2.8, AC-2.6, AC-3.13). Moved to Phase 2: D5 and D6. No further project documents; from now on change requests may only remove scope. Must total now about 34.5 h |
| 1.4 | 2026-11-13 | CR-6, requested by the project owner: the assistant writes the analysis code (metric calculation, robustness tests, shortlist rule, charts, pipeline wiring and their tests). The owner does not write Python and does not aim at roles that require it. G-7 is changed accordingly. G-6 still applies: the owner reads the code with a guided walk-through and must be able to explain what it does. The owner's own contributions are the decisions and their reasoning, the spot-check of the query ratings, the adoption research, the scores and their evidence, the interpretation and the write-ups. The repository states this division of work openly (R-4.3, now in the README). Owner hours for sprint 1 coding are replaced by the walk-through |

---

## 1. How to read this document

- A **requirement** (`R`) says what a deliverable must contain or do.
- An **acceptance criterion** (`AC`) is a check with a yes/no answer. A deliverable is accepted when every one of its criteria is met.
- A **decision** (`OD`) is a choice made by the project owner. Section 9 records them all.
- IDs are stable, so issues, commits and status notes can refer to them (e.g. `AC-2.4`).

This document specifies the **Must** deliverables (D0–D4). The **Could** deliverable (D8) is specified only if it is started.

## 2. Requirements that apply to everything

| ID | Requirement |
|---|---|
| G-1 | All content is in English. |
| G-2 | Data is public or synthetic. Synthetic or illustrative data is labelled as such wherever it appears (file, chart, text). |
| G-3 | Every factual claim has a source, cited with author or organisation, year and link. |
| G-4 | No secrets, API keys, personal data or confidential material in the repository, including its history. |
| G-5 | Every chart has a title, labelled axes with units, and a source note. Colour is never the only way to tell series apart. |
| G-6 | The owner can explain every line of code and every claim (charter, authorship rule). |
| G-7 | The code is written by the AI assistant at the owner's direction (CR-5, CR-6). The owner's judgement, research, scores and written analysis are committed by the owner under their own Git identity. The README states who did what. |

### Definition of Done (per deliverable)

A deliverable is done when:

1. all its acceptance criteria are met;
2. the self-review checklist (section 7) is filled in and every finding is fixed or answered in writing;
3. it is merged into `main` through a pull request;
4. links to it from the README and related documents work.

---

## 3. Must deliverables

### D0 · Requirements research

**Purpose:** check what the target readers actually ask for, so the requirements below rest on evidence.

| ID | Requirement |
|---|---|
| R-0.1 | Collect 10–15 current role descriptions for innovation analyst or closely related roles. |
| R-0.2 | Cover corporate and public-sector employers. Consultancies are not covered by the sample, so conclusions about them are not drawn from D0. |
| R-0.3 | Code each description with one fixed scheme: methods, tools, domain knowledge, soft skills, years of experience. |
| R-0.4 | Produce a frequency table (how many descriptions mention each item) and a half-page conclusion. |
| R-0.5 | Compare the result with D1–D4 and record any gap as a change request to this document. |
| R-0.6 | Keep the raw material and the table outside the public repository. |

| ID | Acceptance criterion |
|---|---|
| AC-0.1 | At least 10 descriptions are coded. |
| AC-0.2 | The frequency table lists the 10 most-requested items per category. |
| AC-0.3 | A written gap check exists: for each of the top 10 methods and tools, it states whether D1–D4 demonstrate it, and what happens if not (change request, Phase 2, or deliberately left out). |
| AC-0.4 | Nothing from D0 appears in the repository except resulting changes to this document. |

### D1 · Thin data pipeline

**Purpose:** one reproducible path from source data to the datasets and charts used by D2 and D3.

| ID | Requirement |
|---|---|
| R-1.1 | Python package `pipelines/` with one module per step: `ingest` (fetch), `transform` (clean, aggregate), `figures` (charts). |
| R-1.2 | One entry point: `python -m pipelines run all`. Single steps can also be run on their own (e.g. `run trends`, `run scoring`). |
| R-1.3 | Folder layout: `data/raw/` (source snapshots), `data/processed/` (analysis-ready CSV), `outputs/figures/` (charts). |
| R-1.4 | Parameters (sub-topics, search terms, years, criteria weights) live in one configuration file, not in the code. |
| R-1.5 | A dated **snapshot** of the raw data is committed. The default run uses the snapshot. A `--refresh` option fetches new data from the source and writes a new snapshot. |
| R-1.6 | Each processed file has a companion note or header stating source, fetch date and the query used. |
| R-1.7 | Dependencies are pinned in `requirements.txt`. The supported Python version is stated. |
| R-1.8 | Unit tests (pytest) cover the transform functions with small fixed inputs. |
| R-1.9 | A GitHub Actions workflow runs the tests and the default pipeline on every pull request. |
| R-1.10 | Scope limit: only what D2 and D3 need. No scheduler, database or extra sources in this phase. |

| ID | Acceptance criterion |
|---|---|
| AC-1.1 | From a fresh clone, the README steps (5 at most) end with `python -m pipelines run all` finishing without error. |
| AC-1.2 | The default run needs no network access and no credentials. |
| AC-1.3 | Running the default pipeline twice leaves `git status` clean: outputs are identical. |
| AC-1.4 | The default run finishes in under 5 minutes on a normal laptop. |
| AC-1.5 | `pytest` passes, with at least one test per transform function. |
| AC-1.6 | The GitHub Actions workflow is green on the pull request that delivers D1. |
| AC-1.7 | Changing a search term or a weight needs an edit in the configuration file only. |
| AC-1.8 | `--refresh` works with any credential supplied through an environment variable (`OPENALEX_API_KEY`, `OPENALEX_MAILTO`); a search of the repository finds no key or token. |

### D2 · Trend scan: AI in industrial manufacturing

**Purpose:** answer the question *"Which AI application areas in industrial manufacturing show the strongest momentum, and which deserve a closer evaluation?"*

| ID | Requirement |
|---|---|
| R-2.1 | Published as `trend-scans/2026-11_ai-in-industrial-manufacturing.md`. |
| R-2.2 | Covers 8–12 sub-topics (application areas), each defined by a documented search query. Decided in OD-2. |
| R-2.3 | Primary data: yearly publication counts per sub-topic from an open bibliographic source (OpenAlex), for complete years only. Decided in OD-3. |
| R-2.4 | Metrics per sub-topic: **volume** (works in the last 3 complete years), **momentum** (compound annual growth over the last 5 complete years) and **relative momentum** (growth compared with the growth of the whole field, so general AI hype is not mistaken for a specific trend). |
| R-2.5 | Charts, all produced by the pipeline: (a) time series per sub-topic; (b) trend radar placing sub-topics by volume and relative momentum. |
| R-2.6 | A query-quality check: for each sub-topic, a sample of 20 results is read and the share of relevant ones is reported. |
| R-2.7 | Interpretation: 2–4 sentences per notable sub-topic on what drives it, using at least one non-bibliographic source (industry report, company announcement, standard). |
| R-2.8 | A **shortlist of at most 8 sub-topics**, selected by the rule in the method note and not padded, with a one-line reason each. This is the input to D3. |
| R-2.9 | A limitations section. It must address at least: publications are not market adoption; keyword bias; time lag; coverage of the data source. |
| R-2.10 | Structure: summary, question, method, results, interpretation, shortlist and recommendation, limitations, sources. |
| R-2.11 | An **adoption level** (0 to 3) per sub-topic from non-academic sources, as a second signal next to publication counts. |
| R-2.12 | A **discovery step**: the fastest-growing topic labels in the field are compared with the ten sub-topics, and what the list missed is reported. |

| ID | Acceptance criterion |
|---|---|
| AC-2.1 | The file opens with a summary of 150 words or fewer that states the question, the main finding and the recommendation. |
| AC-2.2 | Between 8 and 12 sub-topics are covered, and each search query is listed in the document or linked from it. |
| AC-2.3 | Every number in the text can be found in a file in `data/processed/`. |
| AC-2.4 | Both charts are generated by the pipeline and embedded in the document; none is edited by hand. |
| AC-2.5 | The query-quality table is present. Any sub-topic with under 70% relevant results is either re-queried or flagged as unreliable. |
| AC-2.6 | The shortlist has at most 8 items, follows the rule in the method note (any exception is marked), and each item has a reason that refers to a metric or a cited source. |
| AC-2.7 | The limitations section covers the four points in R-2.9. |
| AC-2.8 | Every factual claim outside the project's own data has a source (G-3). |
| AC-2.9 | Only complete calendar years are used; the document states the fetch date. |
| AC-2.10 | `data/manual/adoption.csv` has a level and a cited source for every sub-topic, and the trend map shows the level. |
| AC-2.11 | The document contains the table from the discovery step and names any area the ten sub-topics missed. |
| AC-2.12 | The method note was approved and merged before the first data snapshot was committed (visible in the Git history). |

### D3 · Opportunity scoring model

**Purpose:** rank the D2 shortlist for a defined organisation and give a recommendation that holds up when the assumptions change.

| ID | Requirement |
|---|---|
| R-3.1 | Lives in `tools/opportunity-scoring/` with a guide (`README.md`) and a worked example (the D2 shortlist). |
| R-3.2 | The ranking is made from the viewpoint of a **reference organisation**: a short, illustrative company profile (size, sector, capabilities, strategy), labelled as fictional. Decided in OD-4. |
| R-3.3 | 4–6 criteria, each scored 1–5. Market attractiveness, technical feasibility, strategic fit, time to value, risk (inverted), as decided in OD-5. |
| R-3.4 | A **rubric** defines in words what a 1, 3 and 5 mean for each criterion. |
| R-3.5 | Every score has a one-line justification and a pointer to evidence (a D2 metric or a cited source). |
| R-3.6 | Weights sum to 1 and are stated with a reason. Starting weights are in OD-5. |
| R-3.7 | Sensitivity check: (a) the ranking is recomputed for at least 1,000 random weight sets; (b) each opportunity's share of runs in the top 3 is reported; (c) the weight change that would swap ranks 1 and 2 is stated. |
| R-3.8 | Outputs produced by the pipeline: ranked table, rank-stability chart, and a score-versus-time-horizon chart. |
| R-3.9 | A recommendation that sorts each opportunity into pursue, explore or park, with reasons. |
| R-3.10 | Reusable: another user can swap in their own opportunity list and configuration without changing code. The guide explains how. |
| R-3.11 | A **cost-benefit view** for the two top-ranked opportunities, from the reference organisation's viewpoint: investment range, expected yearly benefit and payback period, each for a cautious, a base and an optimistic case. Every input is either sourced or marked as an assumption. |

| ID | Acceptance criterion |
|---|---|
| AC-3.1 | The guide opens with a summary of 150 words or fewer and ends with the recommendation. |
| AC-3.2 | The input list equals the D2 shortlist; any difference is explained. |
| AC-3.3 | The rubric covers levels 1, 3 and 5 for every criterion. |
| AC-3.4 | Every score in the input file has a justification and an evidence pointer; a test fails if one is missing. |
| AC-3.5 | A test fails if the weights do not sum to 1. |
| AC-3.6 | The sensitivity results (R-3.7 a–c) are reported in the guide, and the random runs use a fixed seed so results repeat. |
| AC-3.7 | Each opportunity is classified as pursue, explore or park, and the classification is consistent with the stated rule (e.g. "pursue = top 3 in at least 70% of runs"). |
| AC-3.8 | A second, made-up input file runs through the model with a configuration change only (demonstrates R-3.10). |
| AC-3.9 | The reference organisation and all scores are labelled as illustrative wherever they appear (G-2). |
| AC-3.10 | The guide contains a cost-benefit table for the two top-ranked opportunities with investment, yearly benefit and payback for three cases. Every input is listed with a source or the word "assumption", and the table is labelled as illustrative. |
| AC-3.11 | The key figures of the reference organisation each cite a published industry statistic. |
| AC-3.12 | The guide reports the test of uncertain scores and names practically tied opportunities. |
| AC-3.13 | The input list has at least five opportunities; where the shortlist is shorter, sub-topics are split into internal use and offering. |

### D4 · Repository presentation

**Purpose:** a reader landing on the repository understands within a minute what is in it and where to look.

| ID | Requirement |
|---|---|
| R-4.1 | The README has a **Highlights** section: one paragraph and one chart each for D2 and D3, with links. |
| R-4.2 | The README has run instructions (see AC-1.1). |
| R-4.3 | The README states how AI assistance was used. |
| R-4.4 | Folder READMEs match what the folders contain; empty folders say what is planned. |
| R-4.5 | The project documents show their final status, and `ROADMAP.md` reflects what was and was not delivered. |
| R-4.6 | The GitHub repository description and topics are set by the owner. |
| R-4.7 | The README Highlights section has a short paragraph on how the project was run (charter, phase gates, requirements with acceptance criteria, sprint backlog), with links. |

| ID | Acceptance criterion |
|---|---|
| AC-4.1 | The Highlights section exists and both chart images render on GitHub. |
| AC-4.2 | A link check over all Markdown files finds no broken internal links. |
| AC-4.3 | The AI-assistance statement is present. |
| AC-4.4 | No placeholder text ("TODO", "planned topics" for delivered items, "lorem") remains in delivered content. |
| AC-4.5 | The licence files are present and referenced from the README. |
| AC-4.6 | The repository description and at least 3 topics are set on GitHub. |
| AC-4.7 | The Highlights section links to the charter, the requirements document and the issue backlog. |

---

## 4. Should deliverables

None in this phase. The Three Horizons write-up (D5) and the case study (D6) were moved to Phase 2 in v1.3.

---

## 5. Traceability: success criteria to acceptance criteria

| Charter success criterion | Checked by |
|---|---|
| 1. Must deliverables meet their criteria | All AC in section 3 |
| 2. One command reproduces everything | AC-1.1, AC-1.2, AC-1.3 |
| 3. Summary and recommendation | AC-2.1, AC-3.1, AC-3.7 |
| 4. Sources and rubric | AC-2.3, AC-2.8, AC-3.3, AC-3.4 |
| 5. Documented self-review | Section 7 |
| 6. Owner can present in 10 minutes | Dry run at M3 (sprint 3) |
| 7. Final sign-off | Closure document |

---

## 6. Plan

### Work breakdown and estimates

Hours are the owner's working time. Review by the assistant is not counted.

| Sprint | Work package | Deliverable | Est. hours |
|---|---|---|---|
| **0** (11–16 Nov) | Review and approve this document; settle the open decisions | | 1.5 |
| | Collect and code role descriptions; gap check | D0 | 3 |
| | Data availability check: source access terms, test queries for 3 sub-topics | D2 | 1 |
| | Local setup: Python, Git identity, clone, first own commit | D1 | 1 |
| | Read and annotate the pipeline scaffolding supplied by the assistant | D1 | 1 |
| | *Sprint total* | | *7.5* |
| **1** (17–23 Nov) | Configuration and snapshot logic on top of the scaffolding | D1 | 1 |
| | Review the fetch implementation; first live fetch; transform for the metrics; tests | D1 | 1.5 |
| | Queries, quality check, metrics, charts | D2 | 3 |
| | Write-up of the trend scan | D2 | 2 |
| | Adoption level for the ten sub-topics | D2 | 1 |
| | Discovery step | D2 | 1 |
| | Own reasoning for the method decisions (review decision D-4) | D2, D3 | 1 |
| | *Sprint total* | | *10.5* |
| **2** (24–30 Nov) | Reference organisation, rubric, scores with evidence | D3 | 3 |
| | Scoring and sensitivity code; tests; charts | D3 | 3 |
| | Guide and recommendation | D3 | 1.5 |
| | Cost-benefit view for the two top-ranked opportunities | D3 | 1.5 |
| | Cited figures for the profile; test of uncertain scores | D3 | 1 |
| | *Sprint total* | | *10* |
| **3** (1–7 Dec) | Self-review of D2 and D3; fixes | D2, D3 | 2 |
| | README highlights (analyses and project approach), link check, statuses | D4 | 2.5 |
| | Presentation dry run | | 1 |
| | Cold-read test of both summaries | D2, D3 | 0.3 |
| | *Sprint total* | | *5.8* |
| **Close** (8 Dec) | Acceptance check and lessons learned | | 1 |

**Total for the Musts: about 34.5 hours**, against a stated minimum of 24 (4 weeks × 6 hours). This needs about 8.5 hours a week, or a later end date. The owner decides which at the sprint 1 review.

### Planning findings

1. **Sprint 1 was overloaded** in the first draft (10 hours against 6). Decided in OD-7: the assistant supplies the pipeline scaffolding (folder layout, entry point, workflow file) in sprint 0, and the owner reads and annotates it before extending it. Sprint 1 is 7.5 hours after CR-5 (v1.2), still above the 6-hour minimum, so the owner should plan extra time that week.
2. **Sprint 3 is the buffer.** Cut list if a sprint overruns, in this order (v1.3): robustness test C; the business case for the second opportunity (keep one); the discovery step.
3. **D5 and D6 moved to Phase 2** (v1.3). No Should deliverables remain in this phase.
4. **Sprints 1 and 2 are both about 10 hours** after the review decisions (v1.3). Each is well above the 6-hour minimum.

### Ways of working

- **Backlog:** one GitHub Issue per work package, labelled with its deliverable (D0–D6) and sprint.
- **Branches and pull requests:** one branch per work package; the owner opens the pull request; the assistant reviews it against the acceptance criteria; the owner merges.
- **Sprint review** (end of each sprint): which acceptance criteria are met, what moves to the next sprint.
- **Status note:** `docs/project/status.md`, five lines per week (done, next, blocked, risks, on track or not).

### Risk register

| ID | Risk | Likelihood | Impact | Response | Trigger to act |
|---|---|---|---|---|---|
| K-1 | Hours needed exceed hours available | High | High | Cut list in planning finding 2; no further documents; change requests may only remove scope | A sprint ends with a Must work package unfinished |
| K-2 | Data source access is restricted (key required, rate limits, terms change) | Medium | High | Check in sprint 0; committed snapshot removes the dependency after the first fetch; fallback source named in sprint 0 | Test queries fail in sprint 0 |
| K-3 | Keyword queries return too much noise | Medium | Medium | Query-quality check (R-2.6); refine or flag | A sub-topic scores under 70% relevant |
| K-4 | Scores in D3 look arbitrary | Medium | High | Rubric, evidence pointer per score, sensitivity check | Self-review cannot trace a score to evidence |
| K-5 | Owner cannot explain parts of the code | Medium | High | Owner writes the analysis code; scaffolding is read and annotated before use; dry run at M3 | Dry run stalls on a "how does this work" question |
| K-6 | Scope creep | Medium | Medium | Change control; new ideas go to the Phase 2 backlog | A new idea would add more than 1 hour |
| K-7 | No external review | Certain (accepted) | Medium | Documented self-review plus assistant review | n/a |
| K-8 | Local setup problems (Python, Git) | Low | Medium | Setup is its own work package in sprint 0 | Setup takes more than 2 hours |

---

## 7. Self-review checklist

Filled in for D2 and D3 before their sprint review, and stored with the status note.

1. Is every acceptance criterion met? List each one with yes or no.
2. Read the summary only: does it state the question, the finding and the recommendation?
3. Pick three numbers at random from the text. Can each be found in `data/processed/`?
4. Pick three claims at random. Does each have a working source link?
5. What is the weakest point of the analysis, and is it named in the limitations?
6. What would a sceptical reader ask first? Is it answered?
7. Can I explain each code file without opening it?
8. Assistant review: findings listed, each one fixed or answered.
9. Cold-read test: someone who has not seen the project (or a fresh AI session without context) reads only the summary and states the recommendation and the main weakness. If they cannot, the summary is rewritten.

---

## 8. Out of scope reminders

Carried over from the charter so they are not reopened by accident: no scheduler or database, no paid data, no hosted dashboard, no sectors beyond the lead theme, no patents (OD-3), no portfolio dashboard (moved to Phase 2 in v1.1).

---

## 9. Decisions by the project owner

All decided on 2026-11-11 by accepting the proposals.

| ID | Question | Decision |
|---|---|---|
| OD-1 | Where do the role descriptions for D0 come from, and where is the private material kept? | 2–3 job portals plus career pages of 3–4 target employers; kept in a private folder outside the repository. |
| OD-2 | Which sub-topics does D2 cover? | Predictive maintenance; visual quality inspection; digital twins; generative design; robotics and cobots; process optimisation and control; production planning and scheduling; energy optimisation; additive manufacturing; industrial copilots (large language models on the shop floor). The owner may add or remove sub-topics through change control. |
| OD-3 | Data source and time window for D2? Publications only, or patents as well? | OpenAlex; complete years 2015–2025; publications only. Patents go to Phase 2. |
| OD-4 | Which reference organisation does D3 score for? | A fictional mid-sized European machinery manufacturer (about 2,000 staff, strong mechanical engineering, limited in-house data science).  |
| OD-5 | Which criteria and weights does D3 use? | The five criteria in R-3.3. Starting weights: market 0.25, feasibility 0.25, strategic fit 0.20, time to value 0.15, risk 0.15. The owner may adjust the weights during D3 and records the reason. |
| OD-6 | Scripts or notebooks? | Scripts for the pipeline; write-ups in Markdown with embedded charts. No notebooks in this phase, which keeps outputs reproducible and reviews simple. |
| OD-7 | How is the sprint 1 overload handled? | The assistant provides scaffolding and the skeleton moves to sprint 0 (see planning finding 1). |
| OD-8 | Which operating system and Python setup does the owner work on? | Python 3.12 in a virtual environment. The operating system is confirmed during the local setup work package, and the setup instructions are written for it. |

---

## 10. Approval

| Role | Decision | Date |
|---|---|---|
| Project owner | ☑ Approved | 2026-11-11 |
