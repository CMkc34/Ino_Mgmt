# 01 · Project Charter

| | |
|---|---|
| **Project** | Ino_Mgmt: applied innovation analysis |
| **Version** | 1.3 |
| **Status** | Approved |
| **Date** | 2026-11-13 |
| **Project owner / sponsor** | Repository owner |

### Change history

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-11-10 | First draft |
| 0.2 | 2026-11-11 | Added role split and authorship rule; added requirements research (D0); prioritised deliverables (Must / Should / Could); reordered work into one storyline with a lead theme; lightened the process; made success criteria testable; added external reviewers |
| 1.0 | 2026-11-11 | Approved by the project owner with one change: external review is deferred (no reviewers planned for this phase) and replaced by a structured self-review; licence decided (MIT for code, CC BY 4.0 for text); assumptions confirmed |
| 1.1 | 2026-11-12 | Change approved by the project owner after the requirements research: portfolio dashboard (D7) moved to Phase 2; a cost-benefit view added to D3. Details in the requirements document, v1.1 |
| 1.2 | 2026-11-12 | After the design review: Three Horizons write-up (D5) and case study (D6) moved to Phase 2; an adoption signal and a discovery step added to D2. Details in the requirements document, v1.3 |
| 1.3 | 2026-11-13 | Scope extended by the project owner (change request CR-7 in the requirements document): Three Horizons write-up (D5) and case study (D6) back in scope; added a German one-page summary (D9) and a second trend scan (D10). All four are additions beyond the Must deliverables |

---

## 1. Background

Innovation management is often taught through frameworks, but organisations need those frameworks applied to real data to support decisions. This project builds a small set of reproducible, data-driven analyses that show how to do that.

## 2. Objective

By **8 December 2026**, publish a connected set of analyses on **one lead theme**, built on a shared, reproducible data pipeline: a trend scan that identifies opportunities from open data, and a scoring model that ranks them and ends in a recommendation.

**Lead theme (proposed):** AI in industrial manufacturing. It combines two focus sectors (tech / AI and industry & energy). Health & life sciences follows in Phase 2 by reusing the same pipeline and method.

## 3. Storyline

The deliverables build on each other, so the repository reads as one piece of work:

1. **Trend scan:** which sub-topics are growing, measured with open data → a shortlist of opportunities
2. **Scoring model:** ranks that shortlist on weighted criteria → a recommendation
3. **Case study:** a public company pursuing one of the top-ranked opportunities
4. **Portfolio dashboard** (Phase 2): how such opportunities would be tracked as a portfolio

## 4. Scope

Priorities follow MoSCoW. **Must** items define project success. **Should** items are delivered if the Musts are on track. **Could** items are done only with spare time; otherwise they move to Phase 2.

| ID | Priority | Deliverable | Summary |
|---|---|---|---|
| D0 | Must | Requirements research | Review of 10–15 current role descriptions for innovation analysts: which skills, methods and tools are asked for. Input to the requirements; kept private unless the owner decides to publish it |
| D1 | Must | Thin data pipeline | Shared Python pipeline (ingest → clean → processed data), run by one command. Only as much as D2 and D3 need |
| D2 | Must | Trend scan | Lead theme measured with open publication or patent data; trend radar; shortlist of opportunities |
| D3 | Must | Opportunity scoring model | Weighted multi-criteria ranking of the D2 shortlist, each score backed by a stated rubric and evidence; sensitivity check; cost-benefit view for the top two; recommendation |
| D4 | Must | Repository presentation | README highlights, run instructions, licence (MIT for code, CC BY 4.0 for text), consistent documentation |
| D5 | Addition | Framework write-up: Three Horizons | Applied to the D3 results. Back in scope in v1.3 |
| D6 | Addition | Case study | One public company, two frameworks. Back in scope in v1.3 |
| D7 | Moved to Phase 2 | Portfolio dashboard | Removed from this phase in v1.1 |
| D8 | Could | Framework write-up: Technology S-curve | Used to interpret D2 |
| D9 | Addition | German one-page summary | Both analyses on one page, in German. Added in v1.3 |
| D10 | Addition | Second trend scan | Another sector, reusing the pipeline and the method. Added in v1.3 |

### Out of scope (for this phase)

- Trend scans and case studies beyond the lead theme (Phase 2 in [`ROADMAP.md`](../../ROADMAP.md))
- Portfolio dashboard (D7, moved to Phase 2 in v1.1)
- Paid or proprietary data sources
- Web apps or hosted dashboards
- Content in languages other than English, except the German one-page summary (D9)

## 5. Roles and authorship

| Role | Who | Responsibility |
|---|---|---|
| Project owner and author | Repository owner | Sets priorities; makes the analytical judgement calls; writes conclusions and recommendations; commits the work; approves documents and deliverables |
| Reviewer and pair programmer | AI assistant (Claude Code) | Explains methods, proposes structure, reviews drafts and code, helps debug, drafts project documents for approval |
| External reviewers | None planned for this phase | Optional. If a reviewer becomes available, their feedback is handled through change control |
| Target readers | Innovation, strategy and consulting professionals | Their needs, evidenced by D0, shape the requirements |

**Authorship rule:** the owner must be able to explain every line of code and every claim in a published deliverable. Analysis content is committed by the owner. AI assistance is used and stated openly in the README.

## 6. Constraints

- **Time:** 4 weeks (11 Nov to 8 Dec 2026); at least 6 hours a week from the owner
- **Data:** public or synthetic only; synthetic data is always labelled
- **Tools:** Python (pipeline, analysis)
- **Publication:** public repository, so no confidential, copyrighted or personal content
- **Language:** English; one German summary page (D9)

## 7. Assumptions (confirmed by the owner on 2026-11-11)

- "Pipeline" means a **data pipeline** (D1), not an idea funnel or stage-gate design.
- The lead theme is AI in industrial manufacturing.
- Open data sources such as OpenAlex give enough coverage for D2.
- No course assignment or thesis work can be reused as a deliverable. If one can, the scope is adjusted.

## 8. Key risks

| Risk | Impact | Mitigation |
|---|---|---|
| Scope too large for the available hours | Musts not finished | MoSCoW priorities; sprint 3 doubles as buffer for the Musts |
| Too much time on infrastructure or project paperwork | Little visible output | Thin pipeline; lightweight process (see [`README.md`](README.md)) |
| Open data too sparse or noisy for the trend scan | D2 weaker, D3 has no input | Check data availability in sprint 0; name a fallback source |
| Owner cannot explain parts of the work | Credibility | Authorship rule; owner writes and commits analysis content |
| Scope creep | Delay | Change control: new ideas go to Phase 2 unless approved |
| No external review in this phase | Blind spots stay unnoticed | Structured self-review against the acceptance criteria, plus an AI review, before each sprint review; external review remains an option for Phase 2 |

## 9. Schedule

| Sprint | Dates | Goal | Milestone |
|---|---|---|---|
| 0 | 11–16 Nov | Charter approved; D0; requirements and plan approved; data availability check | M0: ready to build (16 Nov) |
| 1 | 17–23 Nov | D1 thin pipeline and D2 trend scan | M1: sprint review (23 Nov) |
| 2 | 24–30 Nov | D3 scoring model | M2: sprint review (30 Nov) |
| 3 | 1–7 Dec | Buffer for Musts; D4; self-review and fixes | M3: sprint review (7 Dec) |
| | 8 Dec | Final acceptance and lessons learned | M4: project closed |

## 10. Success criteria

The project succeeds when all of the following are true:

1. All **Must** deliverables (D0–D4) meet their acceptance criteria, defined in `02-requirements-and-plan.md`.
2. From a fresh clone, following the README, one command reproduces every processed dataset and chart with no manual steps.
3. D2 and D3 each open with a summary of 150 words or fewer and end with an explicit recommendation.
4. Every factual claim in D2 and D3 has a cited source; every score in D3 traces to a stated rubric.
5. D2 and D3 have each passed a documented self-review against their acceptance criteria, with every finding either fixed or answered in writing.
6. The owner can present D2 and D3 without notes in 10 minutes, including how the code works (checked in a dry run at M3).
7. The owner signs off final acceptance by 8 December 2026.

## 11. Approval

| Role | Decision | Date |
|---|---|---|
| Project owner | ☑ Approved with changes (see change history, v1.0) | 2026-11-11 |
