# Architecture

`retail insights` uses a small, local-first architecture. The goal is to make the full analytics workflow easy to understand, easy to run, and easy to extend.

## Overview

The project has four main layers:

1. Data pipeline
2. SQLite analytics database
3. FastAPI service
4. Streamlit dashboard

Each layer has a clear responsibility. Pipeline scripts prepare the data, SQLite stores the analytics table, FastAPI serves JSON metrics, and Streamlit displays those metrics for users.

## Data Flow

```text
Public CSV URL
      |
      v
pipeline/ingest.py
      |
      v
data/raw/source_data.csv
      |
      v
pipeline/clean.py
      |
      v
data/processed/clean_data.csv
data/processed/quality_report.json
      |
      v
pipeline/quality_checks.py
      |
      v
pipeline/load.py
      |
      v
analytics.db / sales_data
      |
      v
app/services/analytics.py
      |
      v
FastAPI endpoints
      |
      v
Streamlit dashboard
```

## Pipeline Layer

The pipeline layer lives in `pipeline/`.

- `ingest.py` downloads a public CSV and saves it as raw data.
- `clean.py` prepares the data for analytics by standardizing columns, removing duplicates, filling missing values, and writing a quality report.
- `quality_checks.py` validates the cleaned dataset and prints a readable summary.
- `load.py` loads the cleaned data into SQLite.

The scripts are designed to be run one at a time from the command line. This keeps the workflow transparent for beginners.

## Storage Layer

The project uses SQLite through `analytics.db`.

SQLite is a good fit for this starter project because it:

- Requires no separate database server
- Stores data in a single local file
- Works well with pandas
- Is easy to inspect with common database tools

The cleaned data is loaded into a table named `sales_data`.

## API Layer

The FastAPI app lives in `app/`.

- `app/main.py` creates the FastAPI application.
- `app/routes/` defines HTTP endpoints.
- `app/services/analytics.py` contains SQL query logic.

The API returns JSON responses for health checks, KPIs, trends, top categories, top products, and anomalies. Route files stay small by delegating database work to the service layer.

## Dashboard Layer

The Streamlit dashboard lives in `dashboards/streamlit_app.py`.

The dashboard reads from the FastAPI endpoints when the API server is running. If the API is unavailable, it falls back to reading from SQLite through the analytics service. This makes the dashboard easier to demo because it can still work with only the database present.

## Testing

Tests live in `tests/`.

The test suite focuses on:

- Data cleaning behavior
- Quality check helper functions
- Core API endpoints

The tests use small in-memory sample datasets and mocked API service functions where possible. This keeps them fast, simple, and independent of a live database.

## Extension Ideas

Good next steps include:

- Adding more API endpoints for customer or product analysis
- Saving quality check reports to JSON
- Adding a Makefile or task runner for pipeline commands
- Adding sample data for demos and tests
- Moving configuration values into environment variables
