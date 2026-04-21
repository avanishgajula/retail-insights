import pandas as pd

from pipeline.quality_checks import (
    check_duplicate_rows,
    check_invalid_dates,
    check_negative_sales_values,
    check_null_values,
    find_date_columns,
    find_sales_columns,
    run_quality_checks,
)


def make_sample_data() -> pd.DataFrame:
    """Create a small DataFrame with common data quality issues."""
    return pd.DataFrame(
        {
            "order_date": ["2026-01-01", "not-a-date", "2026-01-01"],
            "category": ["Coffee", None, "Coffee"],
            "product": ["Latte", "Tea", "Latte"],
            "total_sales": [10.0, -5.0, 10.0],
        }
    )


def test_find_date_columns() -> None:
    data = make_sample_data()

    assert find_date_columns(data) == ["order_date"]


def test_find_sales_columns() -> None:
    data = make_sample_data()

    assert find_sales_columns(data) == ["total_sales"]


def test_check_duplicate_rows() -> None:
    data = make_sample_data()

    result = check_duplicate_rows(data)

    assert result["passed"] is False
    assert result["duplicate_rows"] == 1


def test_check_null_values() -> None:
    data = make_sample_data()

    result = check_null_values(data)

    assert result["passed"] is False
    assert result["total_null_values"] == 1
    assert result["null_counts_by_column"]["category"] == 1


def test_check_invalid_dates() -> None:
    data = make_sample_data()

    result = check_invalid_dates(data)

    assert result["passed"] is False
    assert result["total_invalid_dates"] == 1
    assert result["invalid_dates_by_column"]["order_date"] == 1


def test_check_negative_sales_values() -> None:
    data = make_sample_data()

    result = check_negative_sales_values(data)

    assert result["passed"] is False
    assert result["total_negative_values"] == 1
    assert result["negative_values_by_column"]["total_sales"] == 1


def test_run_quality_checks_returns_full_report() -> None:
    data = make_sample_data()

    report = run_quality_checks(data)

    assert report["row_count"] == 3
    assert report["passed"] is False
    assert "duplicate_rows" in report["checks"]
    assert "null_values" in report["checks"]
    assert "invalid_dates" in report["checks"]
    assert "negative_sales_values" in report["checks"]
