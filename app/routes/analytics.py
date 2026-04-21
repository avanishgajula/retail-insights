import sqlite3
from typing import Any, Callable

from fastapi import APIRouter, HTTPException, Query

from app.services import analytics
from app.services.analytics import AnalyticsError

router = APIRouter(tags=["analytics"])


def run_analytics_query(query_function: Callable[[], Any]) -> Any:
    """Run an analytics function and convert failures to JSON API errors."""
    try:
        return query_function()
    except AnalyticsError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except sqlite3.Error as error:
        raise HTTPException(
            status_code=500,
            detail="Database query failed.",
        ) from error


@router.get("/kpis")
def get_kpis() -> dict[str, float]:
    """Return high-level KPI values."""
    return run_analytics_query(analytics.get_total_sales)


@router.get("/trends")
def get_trends() -> list[dict[str, Any]]:
    """Return monthly sales trend data."""
    return run_analytics_query(analytics.get_monthly_sales_trend)


@router.get("/top-categories")
def get_top_categories(
    limit: int = Query(default=5, ge=1, le=100),
) -> list[dict[str, Any]]:
    """Return top sales categories."""
    return run_analytics_query(lambda: analytics.get_top_categories(limit=limit))


@router.get("/top-products")
def get_top_products(
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict[str, Any]]:
    """Return top sales products."""
    return run_analytics_query(lambda: analytics.get_top_products(limit=limit))


@router.get("/anomalies")
def get_anomalies() -> list[dict[str, Any]]:
    """Return sales anomaly records."""
    return run_analytics_query(analytics.get_anomalies)
