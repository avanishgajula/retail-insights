import pandas as pd

from pipeline.clean import clean_data, clean_retail_data, to_snake_case


def test_to_snake_case() -> None:
    assert to_snake_case(" Order Date ") == "order_date"
    assert to_snake_case("Unit Price ($)") == "unit_price"


def test_clean_data_standardizes_and_fills_values() -> None:
    raw_data = pd.DataFrame(
        {
            "Order ID": [1, 1, 2, 3],
            "Order Date": ["2026-01-01", "2026-01-01", "2026-01-02", None],
            "Product": [" Coffee ", " Coffee ", None, "Tea"],
            "Quantity": [2, 2, None, 4],
            "Unit Price": [4.5, 4.5, 3.0, None],
        }
    )

    cleaned, report = clean_data(raw_data)

    assert len(cleaned) == 3
    assert cleaned.loc[0, "product"] == "Coffee"
    assert cleaned.loc[1, "product"] == "unknown"
    assert cleaned.loc[1, "quantity"] == 3.0
    assert cleaned.loc[2, "unit_price"] == 3.75
    assert list(cleaned["total_sales"]) == [9.0, 9.0, 15.0]
    assert report["original_row_count"] == 4
    assert report["cleaned_row_count"] == 3
    assert report["duplicates_removed"] == 1
    assert report["null_counts_before_cleaning"]["Product"] == 1
    assert report["null_counts_after_cleaning"]["product"] == 0


def test_clean_retail_data_returns_cleaned_data_only() -> None:
    raw_data = pd.DataFrame(
        {
            "order_id": [1],
            "product": ["Coffee"],
            "quantity": [2],
            "unit_price": [4.5],
        }
    )

    cleaned = clean_retail_data(raw_data)

    assert list(cleaned["total_sales"]) == [9.0]
