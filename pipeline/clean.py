import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

RAW_DATA_PATH = Path("data/raw/source_data.csv")
CLEAN_DATA_PATH = Path("data/processed/clean_data.csv")
QUALITY_REPORT_PATH = Path("data/processed/quality_report.json")


def to_snake_case(column_name: str) -> str:
    """Convert a column name to simple snake_case."""
    name = column_name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def standardize_column_names(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the data with snake_case column names."""
    cleaned = data.copy()
    cleaned.columns = [to_snake_case(column) for column in cleaned.columns]
    return cleaned


def strip_string_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Remove leading and trailing whitespace from text columns."""
    cleaned = data.copy()
    string_columns = cleaned.select_dtypes(include=["object", "string"]).columns

    for column in string_columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()
        cleaned[column] = cleaned[column].replace("", pd.NA)

    return cleaned


def parse_date_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Parse columns that appear to contain dates."""
    cleaned = data.copy()
    date_columns = [
        column
        for column in cleaned.columns
        if "date" in column or column.endswith("_at")
    ]

    for column in date_columns:
        cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")

    return cleaned


def fill_missing_values(data: pd.DataFrame) -> pd.DataFrame:
    """Fill missing numeric and string values with simple defaults."""
    cleaned = data.copy()
    numeric_columns = cleaned.select_dtypes(include=["number"]).columns
    string_columns = cleaned.select_dtypes(include=["object", "string"]).columns

    for column in numeric_columns:
        median_value = cleaned[column].median()
        fill_value = 0 if pd.isna(median_value) else median_value
        cleaned[column] = cleaned[column].fillna(fill_value)

    for column in string_columns:
        cleaned[column] = cleaned[column].fillna("unknown")

    return cleaned


def add_total_sales_if_possible(data: pd.DataFrame) -> pd.DataFrame:
    """Add total_sales when quantity and unit_price columns are available."""
    cleaned = data.copy()

    if {"quantity", "unit_price"}.issubset(cleaned.columns):
        cleaned["total_sales"] = cleaned["quantity"] * cleaned["unit_price"]

    return cleaned


def build_quality_report(
    original_data: pd.DataFrame,
    cleaned_data: pd.DataFrame,
    duplicates_removed: int,
    null_counts_before: dict[str, int],
) -> dict[str, Any]:
    """Build a small JSON-ready report describing the cleaning results."""
    return {
        "original_row_count": int(len(original_data)),
        "cleaned_row_count": int(len(cleaned_data)),
        "duplicates_removed": int(duplicates_removed),
        "null_counts_before_cleaning": null_counts_before,
        "null_counts_after_cleaning": {
            column: int(count)
            for column, count in cleaned_data.isna().sum().to_dict().items()
        },
    }


def clean_data(data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean raw data and return the cleaned data plus a quality report."""
    original_data = data.copy()
    null_counts_before = {
        column: int(count)
        for column, count in original_data.isna().sum().to_dict().items()
    }

    cleaned = standardize_column_names(original_data)
    cleaned = strip_string_columns(cleaned)

    row_count_before_deduplication = len(cleaned)
    cleaned = cleaned.drop_duplicates()
    duplicates_removed = row_count_before_deduplication - len(cleaned)

    cleaned = parse_date_columns(cleaned)
    cleaned = fill_missing_values(cleaned)
    cleaned = add_total_sales_if_possible(cleaned)
    cleaned = cleaned.reset_index(drop=True)

    report = build_quality_report(
        original_data=original_data,
        cleaned_data=cleaned,
        duplicates_removed=duplicates_removed,
        null_counts_before=null_counts_before,
    )

    return cleaned, report


def clean_retail_data(data: pd.DataFrame) -> pd.DataFrame:
    """Clean a retail-style DataFrame and return only the cleaned data."""
    cleaned, _ = clean_data(data)
    return cleaned


def read_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Read the raw source CSV file."""
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found: {path}")

    return pd.read_csv(path)


def save_outputs(
    cleaned_data: pd.DataFrame,
    quality_report: dict[str, Any],
    data_path: Path = CLEAN_DATA_PATH,
    report_path: Path = QUALITY_REPORT_PATH,
) -> None:
    """Save the cleaned CSV and quality report JSON."""
    data_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_data.to_csv(data_path, index=False)

    with report_path.open("w", encoding="utf-8") as report_file:
        json.dump(quality_report, report_file, indent=2)


def main() -> None:
    """Run the cleaning step from the command line."""
    raw_data = read_raw_data()
    cleaned_data, quality_report = clean_data(raw_data)
    save_outputs(cleaned_data, quality_report)
    print(f"Saved {len(cleaned_data)} cleaned rows to {CLEAN_DATA_PATH}")


if __name__ == "__main__":
    main()
