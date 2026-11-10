# Project Management

This repository is run as a small, structured project. The documents here record how it is scoped, specified, planned and accepted.

## Approach: hybrid

- **Upfront (plan-driven):** scope, requirements and acceptance criteria are agreed before building starts, so "done" is defined in advance.
- **Delivery (agile):** work runs in one-week sprints. Each sprint ends with a reviewed, usable deliverable.

## Lifecycle

| # | Phase | Key output | Document | Status |
|---|---|---|---|---|
| 1 | Initiation | Project charter: why, what, constraints, success criteria | [`01-project-charter.md`](01-project-charter.md) | Draft, awaiting approval |
| 2 | Requirements | Specification and acceptance criteria per deliverable | `02-requirements.md` | Not started |
| 3 | Planning | Work breakdown structure, schedule, risk register | `03-project-plan.md` | Not started |
| 4 | Execution | Weekly sprints, tracked as GitHub Issues | GitHub Issues | Not started |
| 5 | Monitoring & control | Weekly status reports, change requests | `status/`, `04-change-log.md` | Not started |
| 6 | Closure | Acceptance sign-off, lessons learned | `05-closure-report.md` | Not started |

## Rules

- **Phase gates:** a phase starts only after the previous document has been approved by the project owner.
- **Change control:** once a document is approved, scope changes go through a recorded change request (what, why, impact on time and quality, decision).
- **Versioning:** every document carries a version and status (Draft → In review → Approved). Git history provides the audit trail.
