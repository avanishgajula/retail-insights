from pathlib import Path
from typing import Any

import pandas as pd

CLEAN_DATA_PATH = Path("data/processed/clean_data.csv")
DATE_KEYWORDS = ("date", "_at")
SALES_KEYWORDS = ("sales", "price", "revenue", "amount", "total")


def read_cleaned_data(path: Path = CLEAN_DATA_PATH) -> pd.DataFrame:
    """Read the cleaned CSV file."""
    if not path.exists():
        raise FileNotFoundError(f"Cleaned data file not found: {path}")

    return pd.read_csv(path)


def find_date_columns(data: pd.DataFrame) -> list[str]:
    """Find columns that look like date columns based on their names."""
    return [
        column
        for column in data.columns
        if any(keyword in column.lower() for keyword in DATE_KEYWORDS)
    ]


def find_sales_columns(data: pd.DataFrame) -> list[str]:
    """Find numeric columns that look related to sales or money."""
    numeric_columns = data.select_dtypes(include=["number"]).columns
    return [
        column
        for column in numeric_columns
        if any(keyword in column.lower() for keyword in SALES_KEYWORDS)
    ]


def check_duplicate_rows(data: pd.DataFrame) -> dict[str, Any]:
    """Check whether the data contains duplicate rows."""
    duplicate_count = int(data.duplicated().sum())
    return {
        "passed": duplicate_count == 0,
        "duplicate_rows": duplicate_count,
    }


def check_null_values(data: pd.DataFrame) -> dict[str, Any]:
    """Check whether the data contains null values."""
    null_counts = {
        column: int(count)
        for column, count in data.isna().sum().to_dict().items()
    }
    total_nulls = int(sum(null_counts.values()))

    return {
        "passed": total_nulls == 0,
        "total_null_values": total_nulls,
        "null_counts_by_column": null_counts,
    }


def check_invalid_dates(data: pd.DataFrame) -> dict[str, Any]:
    """Check date-like columns for values that cannot be parsed."""
    invalid_counts: dict[str, int] = {}

    for column in find_date_columns(data):
        parsed_dates = pd.to_datetime(data[column], errors="coerce")
        invalid_count = int(parsed_dates.isna().sum())
        invalid_counts[column] = invalid_count

    total_invalid_dates = int(sum(invalid_counts.values()))
    return {
        "passed": total_invalid_dates == 0,
        "date_columns_checked": list(invalid_counts.keys()),
        "invalid_dates_by_column": invalid_counts,
        "total_invalid_dates": total_invalid_dates,
    }


def check_negative_sales_values(data: pd.DataFrame) -> dict[str, Any]:
    """Check sales-related numeric columns for negative values."""
    negative_counts: dict[str, int] = {}

    for column in find_sales_columns(data):
        negative_counts[column] = int((data[column] < 0).sum())

    total_negative_values = int(sum(negative_counts.values()))
    return {
        "passed": total_negative_values == 0,
        "sales_columns_checked": list(negative_counts.keys()),
        "negative_values_by_column": negative_counts,
        "total_negative_values": total_negative_values,
    }


def run_quality_checks(data: pd.DataFrame) -> dict[str, Any]:
    """Run all quality checks and return a dictionary report."""
    checks = {
        "duplicate_rows": check_duplicate_rows(data),
        "null_values": check_null_values(data),
        "invalid_dates": check_invalid_dates(data),
        "negative_sales_values": check_negative_sales_values(data),
    }

    return {
        "row_count": int(len(data)),
        "passed": all(check["passed"] for check in checks.values()),
        "checks": checks,
    }


def print_summary(report: dict[str, Any]) -> None:
    """Print a readable quality check summary to the console."""
    print("Data Quality Summary")
    print("====================")
    print(f"Rows checked: {report['row_count']}")
    print(f"Overall status: {'PASSED' if report['passed'] else 'FAILED'}")
    print()

    for check_name, check_result in report["checks"].items():
        status = "PASSED" if check_result["passed"] else "FAILED"
        print(f"{check_name}: {status}")

        for key, value in check_result.items():
            if key != "passed":
                print(f"  {key}: {value}")

        print()


def main() -> None:
    """Run quality checks from the command line."""
    data = read_cleaned_data()
    report = run_quality_checks(data)
    print_summary(report)


if __name__ == "__main__":
    main()
