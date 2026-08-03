# Ops Report Automator

A practical Python automation project that converts operational CSV or Excel data into a polished management workbook and a shareable HTML report.

## Business problem

Teams often spend hours copying production figures into recurring reports. This tool validates the source data, calculates KPIs, groups performance by day and department, and generates the final reporting package in one command.

## Features

- CSV and XLSX input
- Schema validation with useful error messages
- Production, quality, target and downtime KPIs
- Daily and department summaries
- Styled Excel workbook with dashboard and charts
- Standalone HTML summary
- Command-line interface
- Automated unit and workbook tests
- Docker support and GitHub Actions artifacts

## Quick start

```bash
python -m venv .venv
pip install -r requirements-dev.txt
python -m ops_reporter.cli sample_data/operations_sample.csv --output-dir output
```

Generated files:

- `output/operations_report.xlsx`
- `output/operations_report.html`

## Expected columns

`date`, `department`, `operator`, `units_produced`, `defects`, `downtime_minutes`, `target_units`

## Test

```bash
pytest
ruff check ops_reporter tests
```

## Author

**Tefik Aliu** — https://github.com/tefik-aliu
