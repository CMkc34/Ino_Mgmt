# Roadmap

Content plan for this repository. Focus: **data-driven innovation analysis** and **technology foresight** in three sectors:

- Tech / digital / AI
- Industry & energy
- Health & life sciences

Tooling: **Python** (analysis, notebooks, charts) and **Power BI** (dashboards). All data comes from public sources or is synthetic and clearly labelled as such.

---

## Phase 1: Flagship pieces (weeks 1–4)

### Week 1: Opportunity scoring model
- [ ] `tools/opportunity-scoring/`: Python model that ranks innovation opportunities on weighted criteria (market attractiveness, technical feasibility, strategic fit, time to value, risk)
- [ ] Sensitivity analysis: how the ranking changes when weights change
- [ ] Short guide plus an example using about 10 illustrative opportunities
- [ ] `frameworks/three-horizons.md`: worked example tied to the scoring model

### Week 2: Data-driven trend scan
- [ ] `trend-scans/2026-11_ai-in-industrial-manufacturing.md`
- [ ] Python notebook that pulls publication or patent counts from an open source (e.g. OpenAlex) to measure how fast sub-topics are growing
- [ ] Trend radar chart (sub-topics placed by maturity and momentum)
- [ ] `frameworks/technology-s-curve.md`: used to interpret the results

### Week 3: Case study
- [ ] `case-studies/`: one public company in industry & energy or health, analysed with two frameworks from this repo
- [ ] Includes at least one chart built from public data (e.g. R&D spend or patent activity)

### Week 4: Innovation portfolio dashboard and polish
- [ ] `tools/portfolio-dashboard/`: Power BI dashboard (screenshots plus `.pbix`) on a synthetic innovation portfolio generated with Python
- [ ] KPIs: pipeline by stage, horizon mix, spend versus expected value, time in stage
- [ ] README "Highlights" section linking the four flagship pieces
- [ ] `requirements.txt` and instructions for running the notebooks

---

## Phase 2: Expansion (ongoing)

- [ ] Trend scan: AI in diagnostics / medtech
- [ ] Trend scan: energy transition technologies (e.g. grid storage, hydrogen)
- [ ] Framework write-ups: Stage-Gate, Jobs-to-be-Done, Lean Startup, Open Innovation, Ambidexterity
- [ ] Second case study, in a different sector from the first
- [ ] Monthly trend-scan cadence

---

## Quality bar for every piece

- Ends with a clear **"so what"**: a recommendation or decision it supports
- Sources cited; assumptions stated
- Reproducible: code and data (or the steps to get the data) included
- Readable in 5 minutes, with the details available for anyone who wants them
