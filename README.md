# retail insights

`retail insights` is a beginner-friendly retail analytics project built with Python. It demonstrates a simple end-to-end workflow for downloading data, cleaning it, loading it into SQLite, serving metrics through FastAPI, and viewing those metrics in a Streamlit dashboard.

The project is intentionally small and readable. It is suitable for learning data pipelines, API basics, dashboarding, and testing without needing cloud services or a complex data platform.

## Dashboard Preview

### Retail Sales Overview
<img width="1264" height="904" alt="image" src="https://github.com/user-attachments/assets/2db70494-41c9-4396-bc7d-173f7eb11202" />

### Additional Dashboard View
<img width="1280" height="900" alt="image" src="https://github.com/user-attachments/assets/56e416b5-9b5f-482d-a13d-2feab793d31e" />

## Data Flow

1. `pipeline/ingest.py` downloads a public CSV dataset and saves it to `data/raw/source_data.csv`.
2. `pipeline/clean.py` standardizes column names, removes duplicates, handles missing values, parses date columns, and writes `data/processed/clean_data.csv`.
3. `pipeline/quality_checks.py` checks the cleaned data for duplicates, null values, invalid dates, and negative sales-related values.
4. `pipeline/load.py` loads the cleaned CSV into `analytics.db` in a SQLite table named `sales_data`.
5. `app/services/analytics.py` queries SQLite and returns clean Python dictionaries and lists.
6. `app/main.py` exposes the analytics through FastAPI endpoints.
7. `dashboards/streamlit_app.py` reads from the FastAPI endpoints when available, or falls back to SQLite directly.

## Project Structure

```text
retail insights/
  app/
    main.py                 FastAPI application entry point
    routes/                 API route modules
    services/               Analytics and business logic
    schemas/                API schema definitions
  pipeline/
    ingest.py               Download raw source data
    clean.py                Clean data and write a quality report
    quality_checks.py       Validate cleaned data
    load.py                 Load cleaned data into SQLite
  dashboards/
    streamlit_app.py        Streamlit analytics dashboard
  data/
    raw/                    Raw downloaded data
    processed/              Cleaned data and reports
  tests/                    Pytest unit and API tests
  docs/
    architecture.md         Architecture overview
  requirements.txt
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

## Run the Pipeline

Run the pipeline from the project root:

```bash
python pipeline/ingest.py
python pipeline/clean.py
python pipeline/quality_checks.py
python pipeline/load.py
```

Expected outputs:

- `data/raw/source_data.csv`
- `data/processed/clean_data.csv`
- `data/processed/quality_report.json`
- `analytics.db`

## Run the FastAPI Server

Start the API server:

```bash
uvicorn app.main:app --reload
```

Useful URLs:

- API health check: http://127.0.0.1:8000/health
- API documentation: http://127.0.0.1:8000/docs
- KPI endpoint: http://127.0.0.1:8000/kpis
- Trend endpoint: http://127.0.0.1:8000/trends

## Run the Streamlit Dashboard

Start the dashboard:

```bash
streamlit run dashboards/streamlit_app.py
```

The dashboard tries to read from the FastAPI server first. If the API is not running, it falls back to querying `analytics.db` directly.

## Run Tests

Run the test suite:

```bash
pytest
```

The tests cover:

- Cleaning logic
- Quality check helpers
- Core API endpoints

## Architecture Summary

The project follows a simple layered architecture:

- The `pipeline` layer prepares data and stores it locally.
- The SQLite database acts as a lightweight analytics store.
- The `services` layer contains reusable query logic.
- The `routes` layer exposes that logic through JSON API endpoints.
- The Streamlit dashboard provides a visual interface for the same metrics.

For more detail, see [docs/architecture.md](docs/architecture.md).
