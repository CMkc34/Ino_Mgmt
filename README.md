# Ino_Mgmt

Notes, tools and case work on innovation management.

This repository collects applied material on how organisations find, evaluate and scale new ideas: concise framework write-ups, case analyses of public companies, reusable templates, and periodic trend scans.

## Focus

- **Sectors:** tech / digital / AI, industry & energy, health & life sciences
- **Methods:** data-driven opportunity assessment, technology foresight and trend analysis, innovation portfolio management
- **Tools:** Python

## Structure

| Folder | Contents |
|---|---|
| [`frameworks/`](frameworks/) | Short, practical write-ups of innovation frameworks and when to use them |
| [`case-studies/`](case-studies/) | Analyses of innovation decisions at public companies, based on public sources |
| [`tools/`](tools/) | Reusable templates: scoring matrices, portfolio trackers, KPI sets |
| [`trend-scans/`](trend-scans/) | Dated scans of industries and emerging technologies |
| [`notes/`](notes/) | Learning log and reading notes, written in my own words |
| [`pipelines/`](pipelines/) | Python data pipeline: ingest, transform, figures |
| [`data/`](data/) | Source snapshots (`raw/`) and analysis-ready files (`processed/`) |
| [`outputs/`](outputs/) | Charts produced by the pipeline |
| [`docs/project/`](docs/project/) | Project charter, requirements and plan |

## Approach

- **Applied over theoretical:** every framework comes with an example of using it.
- **Evidence-based:** claims cite public sources; assumptions are stated.
- **Reusable:** templates are meant to be copied and adapted.

## How this work was made

This project was built with an AI assistant (Claude Code), and the division of work is stated here so nothing is misread.

- **By the project owner:** the scope and priorities, the decisions on method (approved before any data was fetched), the checks of the assistant's work, the rules and levels for adoption, the scores and their evidence, the interpretation and the written analyses.
- **By the AI assistant, at the owner's direction:** the Python code and its tests, the data fetch, drafts of the project documents and method notes, a first rating of the search results, the search for and checking of adoption sources, and reviews, including a critical review of its own designs.

The project documents record each decision and change request, and the Git history shows who committed what.

## Running the pipeline

Requires Python 3.12.

```
python -m venv .venv            # then activate it
python -m pip install -r requirements.txt
python -m pytest
python -m pipelines run all
```

Step-by-step instructions for Windows are in [`docs/setup-windows.md`](docs/setup-windows.md). The pipeline reads a stored snapshot of the source data, so a normal run needs no network access. Parameters are in [`config.yaml`](config.yaml).

## Licence

- **Code** (scripts, notebooks, pipeline): [MIT](LICENSE)
- **Text and figures** (write-ups, case studies, trend scans, documentation): [CC BY 4.0](LICENSE-CONTENT.md)

## Status

Work in progress. See the [project charter](docs/project/01-project-charter.md) for scope and schedule, and [`ROADMAP.md`](ROADMAP.md) for the backlog.
