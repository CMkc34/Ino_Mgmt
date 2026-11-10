# 01 · Project Charter

| | |
|---|---|
| **Project** | Ino_Mgmt: applied innovation analysis |
| **Version** | 0.1 |
| **Status** | Draft, awaiting approval |
| **Date** | 2026-11-10 |
| **Project owner / sponsor** | Repository owner |

---

## 1. Background

Innovation management is often taught through frameworks, but organisations need those frameworks applied to real data to support decisions. This project builds a set of reproducible, data-driven analyses that show how to do that.

## 2. Objective

By **8 December 2026**, publish a set of **four flagship analyses** in this repository. They cover opportunity assessment, technology foresight, company case analysis and portfolio reporting, across three sectors (tech / AI, industry & energy, health & life sciences). All of them are built on one shared, reproducible data pipeline.

## 3. Scope

### In scope

| ID | Deliverable | Summary |
|---|---|---|
| D1 | Data pipeline foundation | Shared Python pipeline: ingest → clean → processed datasets, run by one command |
| D2 | Opportunity scoring model | Weighted multi-criteria ranking of about 10 opportunities, with a sensitivity check and a Three Horizons view |
| D3 | Trend scan | AI in industrial manufacturing, measured with open publication or patent data, with a trend radar |
| D4 | Case study | One public company in industry & energy or health, analysed with two frameworks and public data |
| D5 | Portfolio dashboard | Power BI dashboard on a synthetic innovation portfolio produced by the pipeline |
| D6 | Framework write-ups | Three Horizons and Technology S-curve, each tied to D2 or D3 |
| D7 | Repository presentation | README highlights, run instructions, project documentation |

### Out of scope (for this phase)

- Further trend scans and case studies (Phase 2 in [`ROADMAP.md`](../../ROADMAP.md))
- Framework write-ups beyond the two listed
- Paid or proprietary data sources
- Web apps or hosted dashboards (Power BI is delivered as a file plus screenshots)
- Content in languages other than English

## 4. Stakeholders

| Role | Who | Responsibility |
|---|---|---|
| Project owner / sponsor | Repository owner | Sets priorities, approves documents and deliverables, accepts the final result |
| Delivery support | AI assistant (Claude Code) | Drafts documents, builds code and content, reports status |
| Target readers | Innovation, strategy and consulting professionals | Judge quality; their needs shape the requirements |

## 5. Constraints

- **Time:** 4 weeks (10 Nov to 8 Dec 2026); at least 6 hours a week from the owner
- **Data:** public or synthetic only; synthetic data is always labelled as such
- **Tools:** Python (analysis, pipeline) and Power BI (dashboard)
- **Publication:** public repository, so no confidential, copyrighted or personal content
- **Language:** English

## 6. Assumptions

- "Pipeline" means a **data pipeline** (D1). An idea-funnel or stage-gate design is not part of this phase. *(To be confirmed by the owner.)*
- Open data sources such as OpenAlex give enough coverage for D3.
- The owner has access to Power BI Desktop for D5.

## 7. Key risks (initial)

| Risk | Impact | Mitigation |
|---|---|---|
| Too much time on infrastructure, too little visible output | Deadline missed | Thin pipeline first: each sprint must deliver a visible piece |
| Open data too sparse or noisy for the trend scan | D3 weaker | Check data availability in sprint 1; have a fallback source |
| Scope creep (new ideas mid-project) | Delay | Change control: new ideas go to Phase 2 unless formally approved |
| Owner availability drops | Delay | Weekly status review; cut D6 scope before core deliverables |

## 8. Milestones

| Milestone | Target date | Content |
|---|---|---|
| M0: Charter and requirements approved | 13 Nov 2026 | Docs 01–03 approved |
| M1: Sprint 1 review | 17 Nov 2026 | D1 skeleton plus D2 |
| M2: Sprint 2 review | 24 Nov 2026 | D3 plus S-curve write-up |
| M3: Sprint 3 review | 1 Dec 2026 | D4 |
| M4: Final acceptance | 8 Dec 2026 | D5, D7, closure report |

## 9. Success criteria

The project succeeds when:

1. All in-scope deliverables D1–D7 meet their acceptance criteria (defined in `02-requirements.md`).
2. Running the pipeline from a fresh clone, following the README, reproduces all processed datasets and charts without manual steps.
3. Each flagship analysis ends with a clear, evidence-backed recommendation.
4. A reader can understand any flagship piece in about 5 minutes from its summary.
5. Final acceptance is signed off by the project owner by 8 December 2026.

## 10. Approval

| Role | Decision | Date |
|---|---|---|
| Project owner | ☐ Approved ☐ Approved with changes ☐ Rejected | |
