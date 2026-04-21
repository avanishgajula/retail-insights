import sqlite3
from typing import Any

import httpx
import pandas as pd
import streamlit as st

from app.services import analytics
from app.services.analytics import AnalyticsError

API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 3.0


def fetch_api_json(endpoint: str) -> Any:
    """Fetch JSON data from a FastAPI endpoint."""
    url = f"{API_BASE_URL}{endpoint}"
    response = httpx.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60)
def load_dashboard_data() -> tuple[dict[str, Any], str]:
    """Load dashboard data from the API, then fall back to SQLite."""
    try:
        return {
            "kpis": fetch_api_json("/kpis"),
            "trends": fetch_api_json("/trends"),
            "top_categories": fetch_api_json("/top-categories"),
            "top_products": fetch_api_json("/top-products"),
            "anomalies": fetch_api_json("/anomalies"),
        }, "FastAPI"
    except (httpx.HTTPError, ValueError):
        pass

    try:
        return {
            "kpis": analytics.get_total_sales(),
            "trends": analytics.get_monthly_sales_trend(),
            "top_categories": analytics.get_top_categories(),
            "top_products": analytics.get_top_products(),
            "anomalies": analytics.get_anomalies(),
        }, "SQLite"
    except (AnalyticsError, sqlite3.Error) as error:
        return {"error": str(error)}, "Unavailable"


def to_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert API rows into a DataFrame for charts and tables."""
    return pd.DataFrame(rows)


def show_total_sales(kpis: dict[str, Any]) -> None:
    """Show the total sales KPI."""
    total_sales = float(kpis.get("total_sales", 0))
    st.metric("Total Sales", f"${total_sales:,.2f}")


def show_monthly_trend(rows: list[dict[str, Any]]) -> None:
    """Show the monthly sales trend chart."""
    st.subheader("Monthly Sales Trend")
    trend_data = to_dataframe(rows)

    if trend_data.empty:
        st.info("No monthly trend data is available yet.")
        return

    st.line_chart(trend_data, x="month", y="total_sales")


def show_top_categories(rows: list[dict[str, Any]]) -> None:
    """Show the top categories bar chart."""
    st.subheader("Top Categories")
    category_data = to_dataframe(rows)

    if category_data.empty:
        st.info("No category data is available yet.")
        return

    st.bar_chart(category_data, x="category", y="total_sales")


def show_top_products(rows: list[dict[str, Any]]) -> None:
    """Show the top products table."""
    st.subheader("Top Products")
    product_data = to_dataframe(rows)

    if product_data.empty:
        st.info("No product data is available yet.")
        return

    st.dataframe(product_data, hide_index=True, use_container_width=True)


def show_anomaly_summary(rows: list[dict[str, Any]]) -> None:
    """Show a short anomaly summary and optional anomaly table."""
    st.subheader("Anomaly Summary")
    anomaly_data = to_dataframe(rows)

    st.metric("Anomalies Found", f"{len(anomaly_data):,}")

    if anomaly_data.empty:
        st.success("No anomalies found in the current data.")
        return

    if "reason" in anomaly_data.columns:
        reason_counts = anomaly_data["reason"].value_counts().reset_index()
        reason_counts.columns = ["reason", "count"]
        st.dataframe(reason_counts, hide_index=True, use_container_width=True)

    with st.expander("View anomaly rows"):
        st.dataframe(anomaly_data, hide_index=True, use_container_width=True)


def main() -> None:
    """Render the Streamlit dashboard."""
    st.set_page_config(page_title="Retail Insights Dashboard", layout="wide")
    st.title("Retail Insights Dashboard")

    dashboard_data, source = load_dashboard_data()

    if "error" in dashboard_data:
        st.error(dashboard_data["error"])
        st.info("Run the pipeline and start the API, or load data into analytics.db.")
        return

    st.caption(f"Data source: {source}")

    show_total_sales(dashboard_data["kpis"])

    left_column, right_column = st.columns(2)

    with left_column:
        show_monthly_trend(dashboard_data["trends"])
        show_top_categories(dashboard_data["top_categories"])

    with right_column:
        show_top_products(dashboard_data["top_products"])
        show_anomaly_summary(dashboard_data["anomalies"])


if __name__ == "__main__":
    main()
