import sqlite3
from pathlib import Path
from typing import Any

DATABASE_PATH = Path("analytics.db")
TABLE_NAME = "sales_data"

SALES_COLUMNS = (
    "total_sales",
    "sales",
    "revenue",
    "amount",
    "total_bill",
    "price",
    "unit_price",
)
DATE_KEYWORDS = ("date", "_at")
CATEGORY_COLUMNS = ("category", "product_category", "department", "segment", "type", "day")
PRODUCT_COLUMNS = ("product", "item", "sku", "name")


class AnalyticsError(RuntimeError):
    """Raised when analytics data cannot be read."""


def get_connection(database_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Create a SQLite connection for the analytics database."""
    if not database_path.exists():
        raise AnalyticsError(f"Database not found: {database_path}")

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def quote_identifier(identifier: str) -> str:
    """Safely quote a SQLite table or column identifier."""
    escaped_identifier = identifier.replace('"', '""')
    return f'"{escaped_identifier}"'


def get_table_columns(connection: sqlite3.Connection) -> list[str]:
    """Return column names from the sales_data table."""
    rows = connection.execute(f"PRAGMA table_info({quote_identifier(TABLE_NAME)})").fetchall()
    columns = [row["name"] for row in rows]

    if not columns:
        raise AnalyticsError(f"Table not found or empty schema: {TABLE_NAME}")

    return columns


def find_first_matching_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    """Find the first available column from a list of candidate names."""
    normalized_columns = {column.lower(): column for column in columns}

    for candidate in candidates:
        if candidate in normalized_columns:
            return normalized_columns[candidate]

    return None


def find_date_column(columns: list[str]) -> str | None:
    """Find a column that looks like a date column."""
    for column in columns:
        column_name = column.lower()
        if any(keyword in column_name for keyword in DATE_KEYWORDS):
            return column

    return None


def find_sales_column(columns: list[str]) -> str | None:
    """Find the best numeric column to use for sales metrics."""
    return find_first_matching_column(columns, SALES_COLUMNS)


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a SQLite row into a plain dictionary."""
    return dict(row)


def get_total_sales() -> dict[str, float]:
    """Return total sales from the analytics database."""
    with get_connection() as connection:
        columns = get_table_columns(connection)
        sales_column = find_sales_column(columns)

        if sales_column is None:
            return {"total_sales": 0.0}

        query = f"""
            SELECT COALESCE(SUM({quote_identifier(sales_column)}), 0) AS total_sales
            FROM {quote_identifier(TABLE_NAME)}
        """
        row = connection.execute(query).fetchone()

    return {"total_sales": float(row["total_sales"])}


def get_monthly_sales_trend() -> list[dict[str, Any]]:
    """Return monthly sales totals sorted by month."""
    with get_connection() as connection:
        columns = get_table_columns(connection)
        sales_column = find_sales_column(columns)
        date_column = find_date_column(columns)

        if sales_column is None or date_column is None:
            return []

        query = f"""
            SELECT
                strftime('%Y-%m', {quote_identifier(date_column)}) AS month,
                COALESCE(SUM({quote_identifier(sales_column)}), 0) AS total_sales
            FROM {quote_identifier(TABLE_NAME)}
            WHERE {quote_identifier(date_column)} IS NOT NULL
            GROUP BY month
            ORDER BY month
        """
        rows = connection.execute(query).fetchall()

    return [
        {"month": row["month"], "total_sales": float(row["total_sales"])}
        for row in rows
        if row["month"] is not None
    ]


def get_top_categories(limit: int = 5) -> list[dict[str, Any]]:
    """Return top categories by total sales."""
    with get_connection() as connection:
        columns = get_table_columns(connection)
        sales_column = find_sales_column(columns)
        category_column = find_first_matching_column(columns, CATEGORY_COLUMNS)

        if sales_column is None or category_column is None:
            return []

        query = f"""
            SELECT
                {quote_identifier(category_column)} AS category,
                COALESCE(SUM({quote_identifier(sales_column)}), 0) AS total_sales
            FROM {quote_identifier(TABLE_NAME)}
            GROUP BY {quote_identifier(category_column)}
            ORDER BY total_sales DESC
            LIMIT ?
        """
        rows = connection.execute(query, (limit,)).fetchall()

    return [
        {"category": row["category"], "total_sales": float(row["total_sales"])}
        for row in rows
    ]


def get_top_products(limit: int = 10) -> list[dict[str, Any]]:
    """Return top products by total sales."""
    with get_connection() as connection:
        columns = get_table_columns(connection)
        sales_column = find_sales_column(columns)
        product_column = find_first_matching_column(columns, PRODUCT_COLUMNS)

        if sales_column is None or product_column is None:
            return []

        query = f"""
            SELECT
                {quote_identifier(product_column)} AS product,
                COALESCE(SUM({quote_identifier(sales_column)}), 0) AS total_sales
            FROM {quote_identifier(TABLE_NAME)}
            GROUP BY {quote_identifier(product_column)}
            ORDER BY total_sales DESC
            LIMIT ?
        """
        rows = connection.execute(query, (limit,)).fetchall()

    return [
        {"product": row["product"], "total_sales": float(row["total_sales"])}
        for row in rows
    ]


def get_anomalies() -> list[dict[str, Any]]:
    """Return rows with unusually high or negative sales values."""
    with get_connection() as connection:
        columns = get_table_columns(connection)
        sales_column = find_sales_column(columns)

        if sales_column is None:
            return []

        sales_identifier = quote_identifier(sales_column)
        table_identifier = quote_identifier(TABLE_NAME)
        stats_query = f"""
            SELECT
                AVG({sales_identifier}) AS average_sales
            FROM {table_identifier}
        """
        stats = connection.execute(stats_query).fetchone()
        average_sales = float(stats["average_sales"] or 0)
        high_sales_threshold = average_sales * 3 if average_sales > 0 else None

        if high_sales_threshold is None:
            anomaly_query = f"""
                SELECT rowid AS row_id, *
                FROM {table_identifier}
                WHERE {sales_identifier} < 0
                ORDER BY {sales_identifier} ASC
                LIMIT 50
            """
            rows = connection.execute(anomaly_query).fetchall()
        else:
            anomaly_query = f"""
                SELECT rowid AS row_id, *
                FROM {table_identifier}
                WHERE {sales_identifier} < 0
                   OR {sales_identifier} >= ?
                ORDER BY {sales_identifier} DESC
                LIMIT 50
            """
            rows = connection.execute(anomaly_query, (high_sales_threshold,)).fetchall()

    anomalies = []
    for row in rows:
        anomaly = row_to_dict(row)
        sales_value = float(anomaly[sales_column])
        anomaly["reason"] = "negative_sales" if sales_value < 0 else "unusually_high_sales"
        anomalies.append(anomaly)

    return anomalies
