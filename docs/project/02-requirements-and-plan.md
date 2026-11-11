# 02 · Requirements and Plan

| | |
|---|---|
| **Project** | Ino_Mgmt: applied innovation analysis |
| **Version** | 0.1 |
| **Status** | Draft, awaiting approval |
| **Date** | 2026-11-11 |
| **Based on** | [Project charter v1.0](01-project-charter.md) |

### Change history

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-11-11 | First draft |

---

## 1. How to read this document

- A **requirement** (`R`) says what a deliverable must contain or do.
- An **acceptance criterion** (`AC`) is a check with a yes/no answer. A deliverable is accepted when every one of its criteria is met.
- An **open decision** (`OD`) is a choice the project owner has to make. Each one comes with a proposal. Section 9 lists them all.
- IDs are stable, so issues, commits and status notes can refer to them (e.g. `AC-2.4`).

This document specifies the **Must** deliverables (D0–D4) in full and the **Should** deliverables (D5, D6) in outline. **Could** deliverables (D7, D8) are specified only if they are started.

## 2. Requirements that apply to everything

| ID | Requirement |
|---|---|
| G-1 | All content is in English. |
| G-2 | Data is public or synthetic. Synthetic or illustrative data is labelled as such wherever it appears (file, chart, text). |
| G-3 | Every factual claim has a source, cited with author or organisation, year and link. |
| G-4 | No secrets, API keys, personal data or confidential material in the repository, including its history. |
| G-5 | Every chart has a title, labelled axes with units, and a source note. Colour is never the only way to tell series apart. |
| G-6 | The owner can explain every line of code and every claim (charter, authorship rule). |
| G-7 | Analysis content is committed by the owner under their own Git identity. |

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
| R-0.2 | Cover both target employer types: consultancies and corporate innovation teams. |
| R-0.3 | Code each description with one fixed scheme: methods, tools, domain knowledge, soft skills, years of experience. |
| R-0.4 | Produce a frequency table (how many descriptions mention each item) and a half-page conclusion. |
| R-0.5 | Compare the result with D1–D4 and record any gap as a change request to this document. |
| R-0.6 | Keep the raw material and the table outside the public repository. |

| ID | Acceptance criterion |
|---|---|
| AC-0.1 | At least 10 descriptions are coded, with at least 4 from each employer type. |
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
| AC-1.8 | `--refresh` works with any credential supplied through an environment variable; a search of the repository finds no key or token. |

### D2 · Trend scan: AI in industrial manufacturing

**Purpose:** answer the question *"Which AI application areas in industrial manufacturing show the strongest momentum, and which deserve a closer evaluation?"*

| ID | Requirement |
|---|---|
| R-2.1 | Published as `trend-scans/2026-11_ai-in-industrial-manufacturing.md`. |
| R-2.2 | Covers 8–12 sub-topics (application areas), each defined by a documented search query. See OD-2. |
| R-2.3 | Primary data: yearly publication counts per sub-topic from an open bibliographic source (proposed: OpenAlex), for complete years only. See OD-3. |
| R-2.4 | Metrics per sub-topic: **volume** (works in the last 3 complete years), **momentum** (compound annual growth over the last 5 complete years) and **relative momentum** (growth compared with the growth of the whole field, so general AI hype is not mistaken for a specific trend). |
| R-2.5 | Charts, all produced by the pipeline: (a) time series per sub-topic; (b) trend radar placing sub-topics by volume and relative momentum. |
| R-2.6 | A query-quality check: for each sub-topic, a sample of 20 results is read and the share of relevant ones is reported. |
| R-2.7 | Interpretation: 2–4 sentences per notable sub-topic on what drives it, using at least one non-bibliographic source (industry report, company announcement, standard). |
| R-2.8 | A **shortlist of 5–8 opportunities** with a one-line reason each. This is the input to D3. |
| R-2.9 | A limitations section. It must address at least: publications are not market adoption; keyword bias; time lag; coverage of the data source. |
| R-2.10 | Structure: summary, question, method, results, interpretation, shortlist and recommendation, limitations, sources. |

| ID | Acceptance criterion |
|---|---|
| AC-2.1 | The file opens with a summary of 150 words or fewer that states the question, the main finding and the recommendation. |
| AC-2.2 | Between 8 and 12 sub-topics are covered, and each search query is listed in the document or linked from it. |
| AC-2.3 | Every number in the text can be found in a file in `data/processed/`. |
| AC-2.4 | Both charts are generated by the pipeline and embedded in the document; none is edited by hand. |
| AC-2.5 | The query-quality table is present. Any sub-topic with under 70% relevant results is either re-queried or flagged as unreliable. |
| AC-2.6 | The shortlist has 5–8 items, each with a reason that refers to a metric or a cited source. |
| AC-2.7 | The limitations section covers the four points in R-2.9. |
| AC-2.8 | Every factual claim outside the project's own data has a source (G-3). |
| AC-2.9 | Only complete calendar years are used; the document states the fetch date. |

### D3 · Opportunity scoring model

**Purpose:** rank the D2 shortlist for a defined organisation and give a recommendation that holds up when the assumptions change.

| ID | Requirement |
|---|---|
| R-3.1 | Lives in `tools/opportunity-scoring/` with a guide (`README.md`) and a worked example (the D2 shortlist). |
| R-3.2 | The ranking is made from the viewpoint of a **reference organisation**: a short, illustrative company profile (size, sector, capabilities, strategy), labelled as fictional. See OD-4. |
| R-3.3 | 4–6 criteria, each scored 1–5. Proposed: market attractiveness, technical feasibility, strategic fit, time to value, risk (inverted). See OD-5. |
| R-3.4 | A **rubric** defines in words what a 1, 3 and 5 mean for each criterion. |
| R-3.5 | Every score has a one-line justification and a pointer to evidence (a D2 metric or a cited source). |
| R-3.6 | Weights sum to 1 and are stated with a reason. See OD-5. |
| R-3.7 | Sensitivity check: (a) the ranking is recomputed for at least 1,000 random weight sets; (b) each opportunity's share of runs in the top 3 is reported; (c) the weight change that would swap ranks 1 and 2 is stated. |
| R-3.8 | Outputs produced by the pipeline: ranked table, rank-stability chart, and a score-versus-time-horizon chart. |
| R-3.9 | A recommendation that sorts each opportunity into pursue, explore or park, with reasons. |
| R-3.10 | Reusable: another user can swap in their own opportunity list and configuration without changing code. The guide explains how. |

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

| ID | Acceptance criterion |
|---|---|
| AC-4.1 | The Highlights section exists and both chart images render on GitHub. |
| AC-4.2 | A link check over all Markdown files finds no broken internal links. |
| AC-4.3 | The AI-assistance statement is present. |
| AC-4.4 | No placeholder text ("TODO", "planned topics" for delivered items, "lorem") remains in delivered content. |
| AC-4.5 | The licence files are present and referenced from the README. |
| AC-4.6 | The repository description and at least 3 topics are set on GitHub. |

---

## 4. Should deliverables (outline)

Full acceptance criteria are written when the deliverable is started.

**D5 · Framework write-up: Three Horizons.** `frameworks/three-horizons.md`, following the five-part structure in `frameworks/README.md`. The worked example places the D3 opportunities on the three horizons and comments on the balance. Target length: 600–900 words. Sources: the original authors are cited.

**D6 · Case study.** One public company pursuing one of the top-ranked D3 opportunities. Six-part structure from `case-studies/README.md`, two frameworks applied, at least one chart from public data produced by the pipeline, and a summary of 150 words or fewer.

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
| | *Sprint total* | | *6.5* |
| **1** (17–23 Nov) | Pipeline skeleton, configuration, snapshot logic | D1 | 2.5 |
| | Ingest and transform for publication counts; tests | D1 | 2.5 |
| | Queries, quality check, metrics, charts | D2 | 3 |
| | Write-up of the trend scan | D2 | 2 |
| | *Sprint total* | | *10* |
| **2** (24–30 Nov) | Reference organisation, rubric, scores with evidence | D3 | 3 |
| | Scoring and sensitivity code; tests; charts | D3 | 3 |
| | Guide and recommendation | D3 | 1.5 |
| | Three Horizons write-up (if on track) | D5 | 2 |
| | *Sprint total* | | *7.5 (9.5 with D5)* |
| **3** (1–7 Dec) | Self-review of D2 and D3; fixes | D2, D3 | 2 |
| | README highlights, link check, statuses | D4 | 2 |
| | Presentation dry run | | 1 |
| | Case study (if on track) | D6 | 5 |
| | *Sprint total* | | *5 (10 with D6)* |
| **Close** (8 Dec) | Acceptance check and lessons learned | | 1 |

**Total for the Musts: about 30 hours**, against a stated minimum of 24 (4 weeks × 6 hours).

### Planning findings

1. **Sprint 1 is overloaded** (10 hours against 6). Options: (a) the owner plans about 10 hours that week; (b) the assistant supplies the pipeline scaffolding (folder layout, entry point, workflow file) for the owner to read and extend, which saves about 2 hours; (c) the pipeline skeleton moves into sprint 0. Proposal: (b) and (c) together. See OD-7.
2. **Sprint 3 is the buffer.** If sprint 1 or 2 overruns, D6 is dropped first, then D5.
3. **D6 is unlikely** within the minimum hours. It stays a Should, with no commitment.

### Ways of working

- **Backlog:** one GitHub Issue per work package, labelled with its deliverable (D0–D6) and sprint.
- **Branches and pull requests:** one branch per work package; the owner opens the pull request; the assistant reviews it against the acceptance criteria; the owner merges.
- **Sprint review** (end of each sprint): which acceptance criteria are met, what moves to the next sprint.
- **Status note:** `docs/project/status.md`, five lines per week (done, next, blocked, risks, on track or not).

### Risk register

| ID | Risk | Likelihood | Impact | Response | Trigger to act |
|---|---|---|---|---|---|
| K-1 | Hours needed exceed hours available | High | High | MoSCoW; drop D6, then D5; scaffolding from the assistant | A sprint ends with a Must work package unfinished |
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

---

## 8. Out of scope reminders

Carried over from the charter so they are not reopened by accident: no scheduler or database, no paid data, no hosted dashboard, no sectors beyond the lead theme, no patents unless OD-3 decides otherwise.

---

## 9. Open decisions for the project owner

| ID | Decision | Proposal |
|---|---|---|
| OD-1 | Where do the role descriptions for D0 come from, and where is the private material kept? | 2–3 job portals plus career pages of 3–4 target employers; kept in a private folder outside the repository. |
| OD-2 | Which sub-topics does D2 cover? | Predictive maintenance; visual quality inspection; digital twins; generative design; robotics and cobots; process optimisation and control; production planning and scheduling; energy optimisation; additive manufacturing; industrial copilots (large language models on the shop floor). The owner adds or removes based on coursework and interest. |
| OD-3 | Data source and time window for D2? Publications only, or patents as well? | OpenAlex; complete years 2015–2025; publications only. Patents go to Phase 2. |
| OD-4 | Which reference organisation does D3 score for? | A fictional mid-sized European machinery manufacturer (about 2,000 staff, strong mechanical engineering, limited in-house data science). Alternative: a profile closer to the owner's own engineering background. |
| OD-5 | Which criteria and weights does D3 use? | The five criteria in R-3.3. Starting weights: market 0.25, feasibility 0.25, strategic fit 0.20, time to value 0.15, risk 0.15. The owner sets the final weights and gives the reason. |
| OD-6 | Scripts or notebooks? | Scripts for the pipeline; write-ups in Markdown with embedded charts. No notebooks in this phase, which keeps outputs reproducible and reviews simple. |
| OD-7 | How is the sprint 1 overload handled? | The assistant provides scaffolding and the skeleton moves to sprint 0 (see planning finding 1). |
| OD-8 | Which operating system and Python setup does the owner work on? | Needed for the setup instructions. Proposal: Python 3.12 in a virtual environment. |

---

## 10. Approval

| Role | Decision | Date |
|---|---|---|
| Project owner | ☐ Approved ☐ Approved with changes ☐ Rejected | |
